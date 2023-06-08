import torch
import torch.fx
from dicp.TopsGraph.opset_transform import topsgraph_opset_transform

class MyModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, input):
        m = torch.nn.Softmax(dim=3)
        output = m(input)
        return output

a = torch.randn(1, 32, 32, 32, dtype=torch.float32)

m = MyModule()
compiled_model = torch.compile(m, backend="topsgraph")
r1 = compiled_model(a)

torch._dynamo.reset()

m = MyModule()
compiled_model = torch.compile(m, backend="inductor")
r2 = compiled_model(a)

print(f'\n****************************\n')

print(f"r1 - r2:\n{r1 - r2}")

print(f"nan test: r1-{torch.isnan(r1).any()}, r2-{torch.isnan(r2).any()}" )
print(f'torch.allclose:\n{torch.allclose(r1, r2)}')
print(f'torch.eq:{torch.eq(r1, r2).all()}')
