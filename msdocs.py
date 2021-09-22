

import os
import sys

from impulse.args import args

from scrapers.base import html
from scrapers.base import tables


command = args.ArgumentParser(complete=True)


def ParseClassNameAndMethods(url):
  content = html.XMLTreeParser().url(url)
  content = next(content.Select(tag='main'))
  unparsedClassname = None
  for h1 in content.Select(tag='h1'):
    unparsedClassname = h1.Content()
  methods = next(content.Select(tag='table'))
  methods = next(methods.Select(tag='tbody'))
  funcs = []
  for method in methods.Select(tag='tr'):
    urlAndMethod = next(method.Select(tag='a'))
    href = urlAndMethod.Attr('href')
    funcs.append(ParseMethodParameters(url, href, urlAndMethod.Content()))
  return unparsedClassname.split()[0], funcs


def ParseMethodParameters(url, methodUrl, methodName):
  newUrl = os.path.dirname(url) + '/' + methodUrl
  content = html.XMLTreeParser().url(newUrl)
  code = next(content.Select(tag='code')).Content()
  codeparts = code.split()
  returnType = codeparts[0]
  args = []
  if len(codeparts) > 2:
    argCount = (len(codeparts) - 3) // 2
    for i in range(argCount):
      argtype = codeparts[2 + i*2].strip()
      argname = codeparts[3 + i*2].strip()
      args.append((argtype, argname))
  return (methodName.split('::')[1], returnType, args)


@command
def generate(url:str):
  """generates a mock class from an msdocs url for d3d11 libraries."""
  className, methods = ParseClassNameAndMethods(url)
  mockName = className[1:] + 'Mock'
  methodStrs = []
  for mName, mRet, mArgs in methods:
    argsStrs = []
    for aType, _ in mArgs:
      argsStrs.append(aType)
    argsFormatted = ', '.join(argsStrs)
    methodStrs.append(
      f'  MOCK_STDCALL_METHOD{len(mArgs)}({mName}, {mRet}({argsFormatted}));')
  methodsFormatted = '\n'.join(methodStrs)

  print(f'''
class {mockName}
    : public Microsoft::WRL::RuntimeClass<
          Microsoft::WRL::RuntimeClassFlags<Microsoft::WRL::ClassicCom>,
          {className}> {{
 public:
  {mockName}();
  ~{mockName}() override;
{methodsFormatted}
}};''')






'''

class D3D11Texture2DMock
    : public Microsoft::WRL::RuntimeClass<
          Microsoft::WRL::RuntimeClassFlags<Microsoft::WRL::ClassicCom>,
          ID3D11Texture2D> {
 public:
  D3D11Texture2DMock();
  ~D3D11Texture2DMock() override;
  MOCK_STDCALL_METHOD1(GetDevice, void(ID3D11Device**));
  MOCK_STDCALL_METHOD3(GetPrivateData, HRESULT(const GUID&, UINT*, void*));
  MOCK_STDCALL_METHOD3(SetPrivateData, HRESULT(const GUID&, UINT, const void*));
  MOCK_STDCALL_METHOD2(SetPrivateDataInterface,
                       HRESULT(const GUID&, const IUnknown*));
  MOCK_STDCALL_METHOD1(GetType, void(D3D11_RESOURCE_DIMENSION*));
  MOCK_STDCALL_METHOD1(SetEvictionPriority, void(UINT));
  MOCK_STDCALL_METHOD0(GetEvictionPriority, UINT());
  MOCK_STDCALL_METHOD1(GetDesc, void(D3D11_TEXTURE2D_DESC*));
};

'''


def main():
  command.eval()