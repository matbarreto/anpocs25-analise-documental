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
- ✅ **Suporte Multi-idioma**: Português, Inglês e Espanhol
- ✅ **Detecção Automática de Idioma**: Identificação inteligente do idioma do conteúdo

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Conexão com internet (para análise de páginas web e ChatGPT)
- API Key da OpenAI (opcional, para funcionalidade ChatGPT)

##  Instalação

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

### Análise com Idioma Específico

```python
# Força o uso de stop words em inglês
analisador = AnalisadorDocumental("documento.pdf", idioma="ingles")

# Força o uso de stop words em espanhol
analisador = AnalisadorDocumental("https://www.exemplo.es", idioma="espanhol")

# Deixa detectar automaticamente (padrão)
analisador = AnalisadorDocumental("documento.pdf")  # Detecta automaticamente
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
print(f"Idioma detectado: {stats['idioma_detectado']}")
```

### Informações da Fonte

```python
# Obtém informações detalhadas da fonte
info = analisador.obter_informacoes_fonte()

if info['tipo'] == 'PDF':
    print(f"Páginas: {info['total_paginas']}")
    print(f"Tamanho: {info['tamanho_bytes']} bytes")
    print(f"Autor: {info['metadados']['autor']}")
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

```
analisador-documental/
├── main.py              # Classe principal AnalisadorDocumental
├── config.py            # Gerenciador de stop words
├── stop_words.json      # Configuração de stop words por idioma
├── requirements.txt     # Dependências do projeto
├── README.md           # Este arquivo
├── LICENSE             # Licença GPL v3
├── exemplo.pdf         # Arquivo de exemplo para testes
└── scripts/            # Scripts adicionais
    └── analise_batch.py # Análise em lote de múltiplos arquivos
```

## 🛠️ Configuração de Stop Words

### Personalizando Stop Words

```python
from config import StopWordsManager

# Cria gerenciador
manager = StopWordsManager()

# Adiciona novas stop words
manager.add_stop_words("ingles", ["custom", "words", "here"])
manager.add_stop_words("portugues", ["palavras", "personalizadas", "aqui"])

# Remove stop words
manager.remove_stop_words("ingles", ["remove", "these", "words"])

# Salva configuração
manager.save_config()
```

### Idiomas Suportados

- **portugues**: Português brasileiro
- **ingles**: Inglês
- **espanhol**: Espanhol

##  Exemplos de Comandos

### Execução Direta
```bash
# Executa o exemplo padrão
python main.py
```

### Execução Interativa
```python
# No Python console ou Jupyter Notebook
from main import AnalisadorDocumental

# Exemplo 1: Análise de PDF
analisador_pdf = AnalisadorDocumental("documento.pdf")
print(analisador_pdf.gerar_relatorio_completo(top_n=20))

# Exemplo 2: Análise de página web
analisador_web = AnalisadorDocumental("https://www.wikipedia.org")
ranking = analisador_web.analisar_frequencia_palavras(top_n=10)
for palavra, freq in ranking:
    print(f"{palavra}: {freq}")

# Exemplo 3: Análise com ChatGPT
prompt = "Identifique os 5 conceitos mais importantes deste conteúdo"
resposta = analisador_web.analisar_com_chatgpt(prompt)
print(resposta)
```

### Scripts Personalizados

**script_analise.py:**
```python
from main import AnalisadorDocumental
import sys

def analisar_fonte(fonte, top_n=15, idioma=None):
    try:
        analisador = AnalisadorDocumental(fonte, idioma=idioma)
        
        print("=== ANÁLISE DOCUMENTAL ===")
        print(f"Fonte: {fonte}")
        print(f"Tipo: {analisador.tipo_fonte}")
        print(f"Idioma: {analisador.idioma_detectado}")
        print()
        
        # Estatísticas
        stats = analisador.obter_estatisticas_gerais()
        print(f"📊 Estatísticas:")
        print(f"   - Palavras totais: {stats['total_palavras']}")
        print(f"   - Palavras únicas: {stats['palavras_unicas']}")
        print(f"   - Densidade vocabular: {stats['densidade_vocabulario']}%")
        print()
        
        # Ranking
        print(f"🏆 Top {top_n} palavras mais frequentes:")
        ranking = analisador.analisar_frequencia_palavras(top_n)
        for i, (palavra, freq) in enumerate(ranking, 1):
            print(f"   {i:2d}. {palavra:<20} ({freq:3d}x)")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script_analise.py <fonte> [top_n] [idioma]")
        print("Exemplos:")
        print("  python script_analise.py documento.pdf 20")
        print("  python script_analise.py https://www.exemplo.com 15 ingles")
        sys.exit(1)
    
    fonte = sys.argv[1]
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    idioma = sys.argv[3] if len(sys.argv) > 3 else None
    
    analisar_fonte(fonte, top_n, idioma)
```

**Execução:**
```bash
python script_analise.py documento.pdf 20
python script_analise.py https://www.wikipedia.org 15 ingles
```

## 🔧 Configurações e Parâmetros

### Parâmetros do Construtor
```python
AnalisadorDocumental(
    fonte="caminho/arquivo.pdf",  # ou URL
    api_key="sua_api_key",        # opcional
    idioma="portugues"            # opcional: "portugues", "ingles", "espanhol"
)
```

### Métodos Principais
```python
# Análise de frequência
analisador.analisar_frequencia_palavras(top_n=10)

# Estatísticas gerais
analisador.obter_estatisticas_gerais()

# Informações da fonte
analisador.obter_informacoes_fonte()

# Relatório completo
analisador.gerar_relatorio_completo(top_n=10)

# Análise com ChatGPT
analisador.analisar_com_chatgpt("seu prompt aqui")
```

## 🛠️ Funcionalidades Detalhadas

### Análise de PDF
- Remove palavras comuns (stop words)
- Filtra palavras muito curtas (< 3 caracteres)
- Normaliza texto (minúsculas, sem pontuação)
- Retorna ranking ordenado por frequência
- Suporte a múltiplas bibliotecas (PyMuPDF, pdfplumber, PyPDF2)

### Análise de Páginas Web
- Extração de texto limpo do HTML
- Remoção de scripts, estilos e elementos de navegação
- Headers personalizados para evitar bloqueios
- Tratamento de timeouts e erros de conexão

### Estatísticas Gerais
- Total de palavras processadas
- Número de palavras únicas
- Densidade de vocabulário
- Tamanho do conteúdo em caracteres
- Tipo de fonte (PDF ou web)
- Idioma detectado automaticamente

### Integração ChatGPT
- Envio de conteúdo + prompt personalizado
- Limitação automática de tokens (4000 chars)
- Tratamento robusto de erros de API
- Configuração flexível de parâmetros

### Gerenciamento de Stop Words
- Configuração externa via JSON
- Suporte a múltiplos idiomas
- Detecção automática de idioma
- Personalização fácil via API

## ⚠️ Limitações e Considerações

### Arquivos PDF
- **Atual**: Suporte a múltiplas bibliotecas
- **Limitação**: PDFs com imagens podem não extrair texto corretamente
- **Criptografia**: Suporte limitado a PDFs criptografados

### Páginas Web
- Requer conexão com internet
- Algumas páginas podem bloquear scraping
- JavaScript dinâmico não é executado
- Rate limiting pode aplicar

### API OpenAI
- Requer conexão com internet
- Consome tokens da sua conta OpenAI
- Rate limiting pode aplicar
- Custo por requisição

### Performance
- Arquivos muito grandes podem ser lentos
- Processamento de texto é feito em memória
- Para arquivos grandes, considere processamento em chunks

## 🐛 Solução de Problemas

### Erro: "Arquivo não encontrado"
- Verifique se o caminho está correto
- Use caminhos absolutos se necessário
- Confirme se o arquivo existe

### Erro: "URL inválida"
- Verifique se a URL está correta
- Certifique-se de incluir o protocolo (http:// ou https://)
- Teste a URL no navegador

### Erro: "Bibliotecas não instaladas"
- Execute: `pip install PyMuPDF requests beautifulsoup4`
- Verifique se as dependências estão instaladas: `pip list`

### Erro: "API key da OpenAI não configurada"
- Configure a variável de ambiente `OPENAI_API_KEY`
- Ou passe a API key no construtor da classe

### Erro de API OpenAI
- Verifique sua conexão com internet
- Confirme se a API key é válida
- Verifique se há créditos na sua conta OpenAI

### Erro de conexão web
- Verifique sua conexão com internet
- Algumas páginas podem bloquear requisições
- Tente com diferentes User-Agents

### Problemas com Stop Words
- Verifique se o arquivo `stop_words.json` existe
- Confirme se o idioma está correto
- Use `manager.save_config()` após modificações

##  Contribuindo

Este projeto está sob licença GPL v3. Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes de Contribuição
- Mantenha o código limpo e bem documentado
- Adicione testes para novas funcionalidades
- Atualize a documentação quando necessário
- Siga as convenções de nomenclatura do projeto

## 📞 Suporte

Para dúvidas, sugestões ou problemas:
- Abra uma issue no repositório
- Consulte a documentação das bibliotecas utilizadas
- Verifique os logs para debug
- Entre em contato com os mantenedores

## 📄 Licença

Este projeto está licenciado sob a GNU General Public License v3.0 - veja o arquivo [LICENSE](LICENSE) para detalhes.

### O que a GPL v3 permite:
- ✅ **Uso comercial**: Pode usar em projetos comerciais
- ✅ **Modificação**: Pode modificar o código
- ✅ **Distribuição**: Pode distribuir cópias
- ✅ **Uso privado**: Pode usar em projetos privados

### O que a GPL v3 exige:
-  **Código aberto**: Modificações devem ser disponibilizadas sob GPL v3
-  **Atribuição**: Deve manter os avisos de copyright originais
- 📄 **Licença**: Deve incluir uma cópia da licença GPL v3
- 🔗 **Linking**: Software que usa este código deve também ser GPL v3

Para mais informações sobre a GPL v3, visite: https://www.gnu.org/licenses/gpl-3.0.html

---

**Desenvolvido com ❤️ para análise documental eficiente e inteligente!**

*Este software é livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da GNU General Public License conforme publicada pela Free Software Foundation, seja a versão 3 da Licença, ou (a seu critério) qualquer versão posterior.*
```
