from common.utils import *

class OpModule(torch.nn.Module):
    def forward(self, a, b):
        res = operator.getitem(a, b)
        return res

model = OpModule()
args = parse_args()
compiled_model = compile_model(model, args.backend, args.dynamic)


class TestGetitem():
    @pytest.mark.parametrize("dtype", [torch.float32])
    @pytest.mark.parametrize("sizes", [Size((5,), (5, 3)), Size((3, 5), (5, 3)), Size((2, 3, 4), (2, 4))])
    @pytest.mark.parametrize("dim", [0, 1, -1])
    @pytest.mark.parametrize("compiled_model", compiled_model)
    def test_operator_getitem(self, sizes, dim, dtype, compiled_model):
        device = get_device()
        size = sizes.dynamic if compiled_model.dynamic else sizes.static
        input1 = torch.randn(size, dtype=dtype)
        input2 = torch.randn(size, dtype=dtype)
        inputs = tuple((input1, input2))

        dicp_input1 = input1.to(device)
        dicp_input2 = input2.to(device)
        dicp_inputs = tuple((dicp_input1, dicp_input2))

        output = model(inputs, dim)
        dynamo.reset()
        update_dynamo_config(compiled_model.dynamic)
        dicp_output = compiled_model.model(dicp_inputs, dim)

        assert torch.allclose(output, dicp_output.cpu(), equal_nan=True)
