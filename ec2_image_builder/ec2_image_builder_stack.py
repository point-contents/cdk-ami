import aws_cdk as cdk

from aws_cdk import (
    Stack,
    aws_imagebuilder as imagebuilder,
    aws_iam as iam,
)

from constructs import Construct

class Ec2ImageBuilderStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, bucket_name: str, base_image: str, image_pipeline_name: str, components_prefix: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_uri = "s3://" + bucket_name + "/" + components_prefix

        component_tmux_uri = bucket_uri + "/install_tmux.yml"

        component_tmux = imagebuilder.CfnComponent(self,
                                                   "component_tmux",
                                                   name="InstallTmux",
                                                   platform="Linux",
                                                   version="1.0.0",
                                                   uri=component_tmux_uri
                                                   )

        component_user_uri = bucket_uri + "/create_user.yml"

        component_user = imagebuilder.CfnComponent(self,
                                                   "component_user",
                                                   name="CreateUser",
                                                   platform="Linux",
                                                   version="1.0.0",
                                                   uri=component_user_uri
                                                   )

        recipe = imagebuilder.CfnImageRecipe(self,
                                            "Alma8CIS1",
                                            name = "Alma8CIS1",
                                            version = "1.0.0",
                                            components = [
                                                {"componentArn": component_tmux.attr_arn},
                                                {"componentArn": component_user.attr_arn}
                                            ],
                                            parent_image = base_image,
											additional_instance_configuration=imagebuilder.CfnImageRecipe.AdditionalInstanceConfigurationProperty(
												systems_manager_agent=imagebuilder.CfnImageRecipe.SystemsManagerAgentProperty(
													uninstall_after_build=False
												),
											),

											block_device_mappings=[imagebuilder.CfnImageRecipe.InstanceBlockDeviceMappingProperty(
												device_name="/dev/xvda",
												ebs=imagebuilder.CfnImageRecipe.EbsInstanceBlockDeviceSpecificationProperty(
													delete_on_termination=True,
													volume_size = 50,
													volume_type = "gp2"
												),
											)],
											working_directory="/opt"
                                            )

        role = iam.Role(self,
                        "BaseServerRole",
                        role_name = "test-instance-profile-name",
                        assumed_by = iam.ServicePrincipal("ec2.amazonaws.com")
                        )

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("EC2InstanceProfileForImageBuilder"))
        role_id = role.role_name
        

        instance_profile = iam.CfnInstanceProfile(self,
                                                  "BaseServerRoleInstanceProfile",
                                                  instance_profile_name = "BaseServerRoleInstanceProfile",
                                                  roles = ["test-instance-profile-name"],
                                                  path = "/"
                                                  )

        instance_profile.node.add_dependency(role)
        instance_profile.add_deletion_override("/")
        instance_profile.add_deletion_override("test-instance-profile-name")
        instance_profile.add_deletion_override(role_id)
        instance_profile.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        
        assert instance_profile is not None


        infrastructure_config = imagebuilder.CfnInfrastructureConfiguration(self,
                                                                            "BaseServerInfrastructureConfig",
                                                                            instance_profile_name = "BaseServerRoleInstanceProfile",
                                                                            name = "infra_config",
                                                                            instance_types=["t2.micro"]
                                                                            )

        infrastructure_config.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        infrastructure_config.add_depends_on(instance_profile)

        pipeline = imagebuilder.CfnImagePipeline(self,
                                                "Alma8CIS1-cdk-test",
                                                name = image_pipeline_name,
                                                image_recipe_arn = recipe.attr_arn,
                                                infrastructure_configuration_arn = infrastructure_config.attr_arn)

        pipeline.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        pipeline.add_depends_on(infrastructure_config)



