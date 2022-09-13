import aws_cdk as core
import aws_cdk.assertions as assertions

from ec2_image_builder.ec2_image_builder_stack import Ec2ImageBuilderStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ec2_image_builder/ec2_image_builder_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = Ec2ImageBuilderStack(app, "ec2-image-builder")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
