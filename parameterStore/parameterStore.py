import aws_cdk as cdk

from aws_cdk import (
    Stack,
	aws_ssm as ssm
)

from constructs import Construct

class parameterStore(Stack):

    def __init__(self, scope: Construct, construct_id: str, parameter_value: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ssm_parameter = ssm.StringParameter(self, "mySsmParameter",
        parameter_name="latest_ami",
        string_value=parameter_value,
        type=ssm.ParameterType.STRING
)
