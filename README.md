# DeBank MCP Server

> Servidor MCP (Model Context Protocol) para integração com a API do DeBank, permitindo consultar dados DeFi através de IA.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-Latest-green.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Sobre

O **DeBank MCP Server** é um servidor MCP que conecta a poderosa API do DeBank com assistentes de IA como o Claude Desktop. Com ele, você pode consultar dados DeFi de forma natural através de conversação, incluindo:

- 💰 Saldos e portfolios de carteiras
- 🪙 Informações de tokens e preços
- 🎨 Coleções de NFTs
- 🏦 Posições em protocolos DeFi
- 📊 Histórico de transações
- 🔒 Análise de segurança de approvals
- ⛽ Preços de gas em tempo real
- E muito mais!

## ✨ Funcionalidades

### Core Tools (4)
- **Chains**: Lista todas as blockchains suportadas (93+ chains)
- **Protocols**: Informações de protocolos DeFi com TVL
- **Tokens**: Preços, metadados e holders de tokens
- **Balance**: Saldo total de carteiras across chains

### Portfolio Tools (5)
- **User Tokens**: Holdings de tokens com paginação
- **User NFTs**: Coleções de NFTs com metadados
- **User Protocols**: Posições DeFi (simple/complex)
- **User History**: Histórico de transações
- **User Approvals**: Análise de segurança de approvals

### Advanced Tools (6)
- **Net Curve**: Tendências de valor em 24h
- **Pool Info**: Analytics de liquidity pools
- **Transaction Simulation**: Simula transações antes de enviar
- **Gas Prices**: Preços de gas por tier
- **Account Units**: Monitoramento de uso da API
- **User Social**: Placeholder para futuro OAuth

**Total**: 15 ferramentas totalmente funcionais!

## 🚀 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Conta no DeBank Cloud (para obter API key)
- Claude Desktop (ou outro cliente MCP)

### Passo 1: Obter API Key do DeBank

1. Acesse [DeBank Cloud](https://cloud.debank.com/)
2. Crie uma conta ou faça login
3. Navegue até a seção de API
4. Copie sua Access Key

### Passo 2: Instalar o Servidor

```bash
# Clone o repositório
git clone https://github.com/caiovicentino/debank-mcp-server.git
cd debank-mcp-server

# Instale as dependências
pip install -e .
```

### Passo 3: Configurar API Key

Crie um arquivo `.env` na raiz do projeto:

```env
DEBANK_ACCESS_KEY=sua_api_key_aqui
```

**⚠️ IMPORTANTE**: Nunca compartilhe ou commit sua API key!

### Passo 4: Testar o Servidor

```bash
# Teste se está funcionando
python -c "from mcp_server_debank.server import mcp; print('✅ Servidor OK!')"
```

## 🔧 Configuração no Claude Desktop

### macOS

1. Edite o arquivo de configuração:
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. Adicione o servidor DeBank:
```json
{
  "mcpServers": {
    "debank": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server_debank.server"
      ],
      "cwd": "/caminho/para/debank-mcp-server",
      "env": {
        "DEBANK_ACCESS_KEY": "sua_api_key_aqui",
        "PYTHONPATH": "/caminho/para/debank-mcp-server/src"
      }
    }
  }
}
```

3. Substitua `/caminho/para/debank-mcp-server` pelo caminho real
4. Substitua `sua_api_key_aqui` pela sua API key do DeBank
5. Reinicie o Claude Desktop

### Windows

1. Edite o arquivo de configuração:
```powershell
notepad %APPDATA%\Claude\claude_desktop_config.json
```

2. Use a mesma configuração acima, ajustando os caminhos para Windows:
```json
{
  "mcpServers": {
    "debank": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server_debank.server"
      ],
      "cwd": "C:\\caminho\\para\\debank-mcp-server",
      "env": {
        "DEBANK_ACCESS_KEY": "sua_api_key_aqui",
        "PYTHONPATH": "C:\\caminho\\para\\debank-mcp-server\\src"
      }
    }
  }
}
```

### Linux

1. Edite o arquivo de configuração:
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

2. Use a mesma configuração do macOS

## 💡 Exemplos de Uso

Após configurar, você pode fazer perguntas naturais no Claude:

### Consultar Saldos
```
Qual é o saldo total da carteira vitalik.eth?
```

### Informações de Tokens
```
Me mostre informações sobre o token USDT na Ethereum
```

### Análise de Portfolio
```
Quais protocolos DeFi a carteira 0x... está usando?
```

### Segurança
```
Liste os approvals de token da carteira 0x... na Ethereum
```

### Gas Prices
```
Qual o preço do gas na Ethereum agora?
```

### NFTs
```
Quantos NFTs a carteira 0x... possui?
```

### Simulação de Transações
```
Simule esta transação antes de enviar: {dados da transação}
```

### Análise de Pools
```
Me dê informações sobre o pool 0x... na Ethereum
```

## 📊 Estrutura do Projeto

```
debank-mcp-server/
├── src/
│   └── mcp_server_debank/
│       ├── __init__.py
│       ├── server.py              # Servidor MCP principal
│       ├── client.py              # Cliente HTTP DeBank
│       ├── validators.py          # Validação de inputs
│       ├── models.py              # Modelos Pydantic
│       ├── portfolio_tools.py     # Tools de portfolio
│       └── advanced_tools.py      # Tools avançados
├── tests/                         # Testes (opcional)
├── pyproject.toml                 # Configuração do projeto
├── .env.example                   # Template de configuração
├── .gitignore                     # Arquivos ignorados
└── README.md                      # Esta documentação
```

## 🔐 Segurança

- ✅ **Nunca** compartilhe sua API key do DeBank
- ✅ Use arquivo `.env` para armazenar credenciais
- ✅ Adicione `.env` ao `.gitignore`
- ✅ Revogue keys comprometidas imediatamente no [DeBank Cloud](https://cloud.debank.com/)
- ✅ Monitore o uso da API regularmente usando a tool `debank_get_account_units`
- ⚠️ Não exponha sua API key em commits, logs ou screenshots
- ⚠️ Use a tool de simulação de transações antes de enviar transações reais

## 🐛 Troubleshooting

### Erro: "DEBANK_ACCESS_KEY not found"
**Solução**: Certifique-se de que o arquivo `.env` existe e contém sua API key, ou que a variável de ambiente está configurada corretamente no `claude_desktop_config.json`.

### Erro: "MCP tool not found"
**Solução**:
1. Reinicie o Claude Desktop completamente (Cmd+Q no macOS e reabra)
2. Verifique se o caminho `cwd` no config está correto
3. Verifique se o `PYTHONPATH` está apontando para o diretório `src`

### Response muito grande
**Solução**: Use os parâmetros de paginação nas ferramentas de portfolio:
- `limit`: Reduzir quantidade de resultados (padrão: 20, máximo: 500)
- `offset`: Paginar através dos resultados

### Erro 401: Unauthorized
**Solução**:
1. Verifique se sua API key está correta
2. Confirme que a key está ativa no [DeBank Cloud](https://cloud.debank.com/)
3. Tente gerar uma nova API key

### Erro 429: Rate Limit
**Solução**:
- O servidor implementa retry automático com backoff exponencial
- Aguarde alguns segundos entre requisições
- Considere fazer upgrade do plano no DeBank Cloud para limites maiores

### Erro: "ModuleNotFoundError: No module named 'mcp_server_debank'"
**Solução**:
1. Certifique-se de ter executado `pip install -e .` no diretório raiz
2. Verifique se o `PYTHONPATH` no config aponta para o diretório `src`
3. Tente reinstalar: `pip uninstall mcp-server-debank && pip install -e .`

### Claude Desktop não está carregando o servidor
**Solução**:
1. Abra o menu Developer no Claude Desktop (View > Developer)
2. Verifique os logs do servidor na aba MCP
3. Confirme que o arquivo de configuração JSON está válido (use um validador JSON)
4. Teste o servidor manualmente: `python -m mcp_server_debank.server`

## 📈 Limites da API

- **Rate Limit**: Varia por plano (até 100 req/s no plano Pro)
- **Paginação**: Máximo 500 items por página (configurável)
- **Chains**: 93+ blockchains suportadas
- **Units**: Cada chamada consome units da sua cota (monitore com `debank_get_account_units`)

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

### Ideias para Contribuições

- 🧪 Adicionar testes unitários e de integração
- 📚 Melhorar documentação e exemplos
- 🐛 Reportar e corrigir bugs
- ✨ Implementar novas ferramentas baseadas em endpoints do DeBank
- 🌐 Adicionar suporte para outros idiomas
- 🔧 Melhorar error handling e validações

## 📝 Changelog

### v1.0.0 (2025-01-11)
- ✅ 15 ferramentas MCP totalmente funcionais
- ✅ Suporte a 93+ blockchains
- ✅ Paginação implementada em todas as tools relevantes
- ✅ Type safety e validação robusta com Pydantic
- ✅ Error handling completo com retry automático
- ✅ Production-ready com logging estruturado
- ✅ Documentação completa em português

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Desenvolvido por Caio Vicentino**

Para as comunidades:
- 🌾 **Yield Hacker** - Maximizando yields em DeFi
- 💰 **Renda Cripto** - Educação financeira crypto
- 🏗️ **Cultura Builder** - Construindo o futuro Web3

## 🔗 Links Úteis

- [DeBank Cloud](https://cloud.debank.com/) - Obtenha sua API key
- [DeBank API Docs](https://docs.cloud.debank.com/) - Documentação oficial da API
- [FastMCP](https://github.com/jlowin/fastmcp) - Framework MCP usado neste projeto
- [Claude Desktop](https://claude.ai/download) - Cliente MCP oficial da Anthropic
- [MCP Protocol](https://modelcontextprotocol.io/) - Especificação do protocolo MCP
- [DeBank Platform](https://debank.com/) - Explore portfolios DeFi

## ⭐ Apoie o Projeto

Se este projeto foi útil para você, considere:
- ⭐ Dar uma estrela no GitHub
- 🐛 Reportar bugs e sugerir melhorias
- 🤝 Contribuir com código
- 📢 Compartilhar com a comunidade
- 💬 Dar feedback sobre sua experiência
- 🎓 Criar tutoriais e conteúdo educativo

---

**Feito com ❤️ para a comunidade Web3 brasileira**
