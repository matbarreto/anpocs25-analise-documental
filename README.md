# 📄 Analisador Documental - Python

Uma classe Python robusta para análise de documentos PDF e páginas web com funcionalidades de processamento de texto e integração com API da OpenAI ChatGPT.

## �� Funcionalidades

- ✅ **Análise de PDFs**: Extração e análise de documentos PDF
- ✅ **Análise de Páginas Web**: Extração e análise de conteúdo web
- ✅ **Análise de Frequência de Palavras**: Ranking das palavras mais frequentes
- ✅ **Estatísticas Gerais**: Métricas detalhadas sobre o conteúdo
- ✅ **Integração com ChatGPT**: Análise inteligente via API da OpenAI
- ✅ **Relatórios Completos**: Geração de relatórios formatados
- ✅ **Processamento de Texto**: Limpeza e normalização automática
- ✅ **Logging Detalhado**: Monitoramento completo das operações

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Conexão com internet (para análise de páginas web e ChatGPT)
- API Key da OpenAI (opcional, para funcionalidade ChatGPT)

## �� Instalação

### 1. Clone ou baixe o projeto
```bash
git clone <url-do-repositorio>
cd analisador-documental
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

**OU instale manualmente:**
```bash
# Para análise de PDFs
pip install PyMuPDF pdfplumber

# Para análise de páginas web
pip install requests beautifulsoup4

# Para funcionalidade ChatGPT (opcional)
pip install requests
```

### 3. Configure a API Key da OpenAI (opcional)
Para usar a funcionalidade de análise com ChatGPT:

**Opção A - Variável de ambiente:**
```bash
# Windows
set OPENAI_API_KEY=sua_api_key_aqui

# Linux/Mac
export OPENAI_API_KEY=sua_api_key_aqui
```

**Opção B - No código:**
```python
analisador = AnalisadorDocumental("fonte", api_key="sua_api_key_aqui")
```

## 📖 Como Usar

### Exemplo Básico

```python
from main import AnalisadorDocumental

# Análise de PDF
analisador_pdf = AnalisadorDocumental("caminho/para/arquivo.pdf")
relatorio_pdf = analisador_pdf.gerar_relatorio_completo()
print(relatorio_pdf)

# Análise de página web
analisador_web = AnalisadorDocumental("https://www.exemplo.com")
relatorio_web = analisador_web.gerar_relatorio_completo()
print(relatorio_web)
```

### Análise de Frequência de Palavras

```python
# Analisa as 15 palavras mais frequentes
ranking = analisador.analisar_frequencia_palavras(top_n=15)

# Exibe o ranking
for i, (palavra, frequencia) in enumerate(ranking, 1):
    print(f"{i}. {palavra}: {frequencia} ocorrências")
```

### Estatísticas Gerais

```python
# Obtém estatísticas do documento
stats = analisador.obter_estatisticas_gerais()

print(f"Total de palavras: {stats['total_palavras']}")
print(f"Palavras únicas: {stats['palavras_unicas']}")
print(f"Densidade de vocabulário: {stats['densidade_vocabulario']}%")
print(f"Tipo de fonte: {stats['tipo_fonte']}")
```

### Informações da Fonte

```python
# Obtém informações detalhadas da fonte
info = analisador.obter_informacoes_fonte()

if info['tipo'] == 'PDF':
    print(f"Páginas: {info['total_paginas']}")
    print(f"Tamanho: {info['tamanho_bytes']} bytes")
else:
    print(f"URL: {info['url']}")
    print(f"Título: {info['titulo']}")
    print(f"Status: {info['status_code']}")
```

### Análise com ChatGPT

```python
# Cria analisador com API key
analisador_chatgpt = AnalisadorDocumental("fonte", api_key="sua_api_key")

# Define um prompt personalizado
prompt = """
Analise este conteúdo e forneça:
1. Principais tópicos discutidos
2. Tom geral do texto (formal, informal, técnico)
3. Público-alvo sugerido
4. Resumo em 3 pontos principais
"""

# Executa a análise
resposta = analisador_chatgpt.analisar_com_chatgpt(prompt)
if resposta:
    print("=== ANÁLISE COM CHATGPT ===")
    print(resposta)
```

## 📁 Estrutura do Projeto
