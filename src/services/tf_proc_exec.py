from datetime import datetime
import json
import os

from subprocess import check_output, STDOUT, CalledProcessError

from cloudshell.api.cloudshell_api import AttributeNameValue
from cloudshell.logging.qs_logger import get_qs_logger, _create_logger

from driver_helper_obj import DriverHelperObject
from models.exceptions import TerraformExecutionError


class TfProcExec(object):
    def __init__(self, driver_helper_obj: DriverHelperObject, tf_workingdir: str):
        self._driver_helper_obj = driver_helper_obj
        self._tf_workingdir = tf_workingdir

        dt = datetime.now().strftime("%d_%m_%y-%H_%M_%S")
        self._exec_output_log = _create_logger(
            log_group=driver_helper_obj.res_id, log_category="QS", log_file_prefix=f"TF_EXEC_LOG_{dt}"
        )

    def init_terraform(self):
        self._driver_helper_obj.logger.info("Performing Terraform Init")
        self._driver_helper_obj.api.WriteMessageToReservationOutput(self._driver_helper_obj.res_id,
                                                                    "Performing Terraform Init...")
        vars = ["init"]
        return self._run_tf_proc_with_command(vars)

    # todo : implement
    def destroy_terraform(self):
        self._driver_helper_obj.logger.info("Performing Terraform Destroy")
        self._driver_helper_obj.api.WriteMessageToReservationOutput(self._driver_helper_obj.res_id,
                                                                    "Performing Terraform Destroy...")
        vars = ["destroy", "-auto-approve", "-no-color"]
        output = self._run_tf_proc_with_command(vars)
        self._write_to_to_exec_log("DESTROY", output)


    def plan_terraform(self):
        self._driver_helper_obj.logger.info("Running Terraform Plan")
        self._driver_helper_obj.api.WriteMessageToReservationOutput(self._driver_helper_obj.res_id,
                                                                    "Generating Terraform Plan...")
        vars = ["plan"]
        if self._driver_helper_obj.tf_service.terraform_inputs:
            for input in self._driver_helper_obj.tf_service.terraform_inputs.split(","):
                vars.append("-var")
                vars.append(f'{input}')
        for var in ["-out", "planfile"]:
            vars.append(var)
        output = self._run_tf_proc_with_command(vars)
        self._write_to_to_exec_log("PLAN", output)

    def apply_terraform(self):
        self._driver_helper_obj.logger.info("Running Terraform Apply")
        self._driver_helper_obj.api.WriteMessageToReservationOutput(self._driver_helper_obj.res_id,
                                                                    "Executing Terraform Apply with auto approve...")
        vars = ["apply", "--auto-approve", "-no-color", "planfile"]

        output = self._run_tf_proc_with_command(vars)
        self._write_to_to_exec_log("PLAN", output)

    def parse_and_save_terraform_outputs(self):
        try:
            self._driver_helper_obj.logger.info("Running 'terraform output -json'")
            vars = ["output", "-json"]
            tf_exec_output = self._run_tf_proc_with_command(vars)

            unparsed_output_json = json.loads(tf_exec_output)
            output_string = []

            for output in unparsed_output_json:
                output_string += [(output + '=' + str(unparsed_output_json[output]['value']))]

            attr_name = f"{self._driver_helper_obj.tf_service.cloudshell_model_name}.Terraform Output"
            attr_req = [AttributeNameValue(attr_name, ",".join(output_string))]
            self._driver_helper_obj.api.SetServiceAttributesValues(self._driver_helper_obj.res_id,
                                                                   self._driver_helper_obj.tf_service.name, attr_req)
        except Exception as e:
            self._driver_helper_obj.logger.error(f"Error occurred while trying to parse Terraform outputs -> {str(e)}")
            raise

    def _run_tf_proc_with_command(self, vars: list):
        tform_command = [f"{os.path.join(self._tf_workingdir,'terraform.exe')}"]
        for var in vars:
            tform_command.append(var)
        try:
            output = check_output(tform_command, cwd=self._tf_workingdir, stderr=STDOUT).decode("utf-8")
            check_output(tform_command, cwd=self._tf_workingdir, stderr=STDOUT).decode("utf-8")
            return output

        except CalledProcessError as e:
            self._driver_helper_obj.logger.error(f"Error occurred while trying to execute Terraform |"
                               f" Output = {e.stdout.decode('utf-8')}")
            raise TerraformExecutionError("Error during Terraform Plan. For more information please look at the logs.",
                                          e.stdout)
        except Exception as e:
            self._driver_helper_obj.logger.error(f"Error Running Terraform plan {str(e)}")
            raise TerraformExecutionError("Error during Terraform Plan. For more information please look at the logs.")

    def _write_to_to_exec_log(self,command: str, log_data: str):
        self._exec_output_log.info(f"-------------------------------------------------=<"
                                   f" {command} START"
                                   f">=-------------------------------------------------\n")
        self._exec_output_log.info(log_data)
        self._exec_output_log.info(f"-------------------------------------------------=<"
                                   f" {command} END"
                                   f">=---------------------------------------------------\n")


