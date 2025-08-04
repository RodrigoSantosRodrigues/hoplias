## 🧠 Agentes IA no Pipeline de Análise de Cromossomos

O sistema é composto por **agentes especializados**, cada um responsável por uma etapa no processamento e análise de imagens cromossômicas, utilizando modelos otimizados localmente via **Ollama**.

## 🐙 Ollama - Plataforma Local para Modelos de IA

**Ollama** é uma plataforma que permite rodar e gerenciar modelos de inteligência artificial de forma local, sem depender de APIs externas. Com Ollama, você pode baixar, armazenar e executar diversos modelos de linguagem e multimodais diretamente no seu ambiente, facilitando integrações seguras, rápidas e privadas.

### Principais Características

- **Execução local de modelos de IA:** evita custos e latência de chamadas externas.
- **Gerenciamento simples de modelos:** comando CLI para baixar, listar, atualizar e remover modelos.
- **Suporte multimodal:** modelos que trabalham com texto, imagens e comandos combinados.
- **Integração facilitada:** funciona bem em pipelines via Docker, scripts e aplicações Python.
- **Segurança e privacidade:** dados e processamento ficam no seu ambiente controlado.

### Como funciona

1. **Instalação:** 
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh


---

### 1. 🧩 Agente de Segmentação

- **Tarefa:** Detectar e isolar cromossomos individuais em uma imagem da metáfase.
- **Modelo:** `llava:13b`
- **Função:** Usa entrada visual + texto para segmentar cromossomos com base na imagem.
- **Vantagens:**
  - Modelo multimodal (imagem + texto).
  - Alta capacidade de descrever e interpretar imagens complexas.
  - Ideal para tarefas iniciais de visão computacional com contexto textual.

---

### 2. 🔄 Agente de Rotacionamento

- **Tarefa:** Corrigir a orientação dos cromossomos detectados (rotação para alinhamento).
- **Modelo:** `openhermes:2.5-mistral`
- **Função:** Raciocina com base em metadados e imagem anotada para sugerir o ângulo ideal de rotação (ex: centrômero centralizado).
- **Vantagens:**
  - Foco em raciocínio analítico e detalhado.
  - Especializado em descrição de etapas, transformações espaciais e decisões baseadas em regras.
  - Leve e responsivo mesmo com prompts longos.

---

### 3. 🏷️ Agente de Classificação

- **Tarefa:** Classificar os cromossomos por tipo, tamanho e morfologia.
- **Modelo:** `llava:13b`
- **Função:** Analisa imagens e rótulos para determinar a classe cromossômica (ex: metacêntrico, submetacêntrico etc).
- **Vantagens:**
  - Reconhecimento visual com contexto anatômico.
  - Boa performance para identificação e descrição de características morfológicas.
  - Compatível com entrada multimodal para apoio textual e visual.

---

### 4. 📊 Agente de Plotagem de Ideograma

- **Tarefa:** Gerar um gráfico de ideograma (ex: com `matplotlib`) a partir dos dados organizados dos cromossomos.
- **Modelo:** `codellama:13b-instruct`
- **Função:** Traduz JSON de cromossomos organizados em código Python (com `matplotlib` ou `plotly`) para visualização final.
- **Vantagens:**
  - Ótima capacidade de geração de código limpo e funcional.
  - Suporte completo a bibliotecas Python para visualização científica.
  - Capacidade de raciocínio lógico e estrutural para desenhar pares cromossômicos corretamente.

---

### FLUXO
AGENTE 1 - Atendimento
- usuário chamou o bot com uma frase.
  - modelo verifica:
    - if enviou imagem.
      - verifica se é uma metáfase
        - enviou - AGENTE 2
        - nao enviou - retorna solicitando "anexe a metáfase"
  usuário anexa a metáfase.
    - if enviou a imagem:
      - verifica se é uma metáfase
        - se for uma metáfase - AGENTE 2
        - não é uma metáfase - retorna solicitando "anexe...
  loop até enviar uma metáfase

AGENTE 2 - segmentação
...


## 📌 Resumo das Escolhas

| Agente         | Tarefa                    | Modelo                    | Por que foi escolhido?                                 |
|----------------|---------------------------|---------------------------|--------------------------------------------------------|
| Segmentação    | Isolar cromossomos        | `llava:13b`               | Multimodal, ótimo para visão computacional             |
| Rotacionamento | Corrigir orientação       | `openhermes:2.5-mistral`  | Raciocínio preciso, ideal para análises lógicas        |
| Classificação  | Determinar classe/morf.   | `llava:13b`               | Interpretação visual + textual                         |
| Ideograma      | Gerar gráfico             | `codellama:13b-instruct`  | Geração de código eficaz e estruturada                |


## mcp comands development

- debug comand line in container
  python -m mcp run mcp_spec.yaml

https://dev.to/pradumnasaraf/run-mcp-servers-in-seconds-with-docker-1ik5
