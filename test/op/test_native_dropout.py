from common.utils import *

class OpModule(torch.nn.Module):
    def forward(self, a, b, train):
        res_default = torch.ops.aten.native_dropout.default(a, b, train)
        return res_default

model = OpModule()
args = parse_args()
compiled_model = compile_model(model, args.backend, args.dynamic)


class TestNativeDropout():
    @pytest.mark.parametrize("dtype", [torch.float32])
    @pytest.mark.parametrize("sizes", [Size((5,), (5, 3)), Size((3, 5), (5, 3)), Size((2, 3, 4), (2, 4))])
    @pytest.mark.parametrize("train", [False, True])
    @pytest.mark.parametrize("compiled_model", compiled_model)
    def test_torch_native_dropout(self, sizes, dtype, train, compiled_model):
        device = get_device()
        size = sizes.dynamic if compiled_model.dynamic else sizes.static
        input1 = torch.randn(size, dtype=dtype)
        value = 0.999

        dicp_input1 = input1.to(device)

        output = model(input1, value, train)
        dynamo.reset()
        update_dynamo_config(compiled_model.dynamic)
        dicp_output = compiled_model.model(dicp_input1, value, train)

        for i, item in enumerate(output):
            assert torch.allclose(item, dicp_output[i].cpu(), equal_nan=True)
