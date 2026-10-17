# ORION 0.4 — nuvem com login Google

**Atualização 0.4:** implementado login Google com validação no servidor. O chat agora exige sessão autenticada. Leia `CONFIGURAR-GOOGLE.md` antes de testar; sem projeto OAuth e servidor publicado, o APK permite somente verificar a interface e o estado de configuração pendente. O modelo e a pesquisa já testados na versão 0.3 foram preservados. Nenhuma hospedagem foi ativada.


**Protótipo funcional de servidor Python + cliente Android compilado. O servidor ainda não foi publicado em uma hospedagem permanente.** O APK de teste precisa de um endereço HTTPS do servidor antes de responder. Não contém um serviço de nuvem ativo embutido.

## O que mudou

Este é um novo projeto baseado na ideia do ORION. O celular envia a pergunta; após validar a sessão Google, o servidor escolhe a especialização, pesquisa páginas públicas, seleciona trechos e gera uma resposta. A conversa mostra fontes e avisos sem exigir abrir um navegador. O modelo fica apenas no servidor: não há download de 491 MB no celular.

A versão de computador pode usar Python. O cliente Android usa Kotlin e usa Credential Manager para entrar com Google. Não acessa e-mail, WhatsApp, contatos ou outros aplicativos.

## Assistentes automáticos

| Perfil | Assuntos principais |
| --- | --- |
| ORION | Questões gerais ou classificação incerta |
| ISAAC | Ciência, física, cosmologia e testes de hipóteses |
| GENIUS | Engenharia, manutenção, equipamentos e programação |
| ATLAS | Pesquisas gerais, notícias e comparações |
| VISION | Escrita e criação |
| SENTINEL | Riscos, golpes e segurança |
| ARCHIVIST | Organização, documentos e resumos |
| NOVA | Estratégia, planejamento e oportunidades |

O roteamento inicial é feito por regras de assunto, sem uma chamada extra ao modelo. O nome escolhido aparece automaticamente na resposta. São especializações do mesmo modelo, não modelos independentes nem agentes conscientes. Perguntas ambíguas podem ser classificadas incorretamente. Os perfis apenas orientam o texto; não executam comandos.

## Pesquisa integrada

- Busca pública no Brave Search, acionada por uma pergunta do usuário. Não utiliza uma API contratada nem oferece garantia de disponibilidade.
- Leitura paralela de até cinco candidatos, seleção de até três fontes e limite de 2 MB por página.
- Seleção de pequenos trechos relevantes para caber no contexto do modelo.
- Filtro de modelos de equipamentos evita misturar, por exemplo, Pit Viper 271 e 275 quando o número é identificado.
- Se a busca ou a leitura falhar, tenta a API da Wikipédia em português e identifica essa limitação.
- Não contorna CAPTCHA, login, paywall ou bloqueios. Não lê PDFs, imagens ou conteúdo que exija JavaScript.
- Se não houver fontes, informa a falha; não apresenta uma resposta supostamente confirmada na web.
- Se o modelo estiver iniciando, pode mostrar trechos identificados como **sem síntese da IA**.
- Os links listados são páginas consultadas; isso não garante que cada frase gerada esteja correta ou sustentada.

A pesquisa pode ser desligada no app. Nesse caso, responde apenas com o modelo e o contexto recente, sem alegar consulta à web.

## Modelo e eficiência

Modelo de referência: **Qwen2.5-1.5B-Instruct-GGUF, Q4_K_M**, Apache 2.0, aproximadamente 1,12 GB no servidor. Motor: llama-cpp-python 0.3.36, MIT. Este modelo é maior que o de 0,5B da base anterior, mas continua sendo um modelo pequeno. Não tem a mesma capacidade do ChatGPT.

O modelo é baixado uma vez, verificado por SHA-256 e mantido carregado. Pesquisa usa leitura paralela e cache de trechos por até cinco minutos. Inferência é serializada para evitar concorrência no mesmo contexto. Há no máximo duas requisições em processamento e limite de oito solicitações por minuto por IP. Em uma instalação atrás de proxy, vários usuários podem compartilhar esse limite; para uma distribuição ampla, configurar limites na entrada e dimensionar os processos/modelos.

Melhor velocidade depende de CPU/GPU, tamanho do modelo, conexões e número de usuários. Não há promessa de atendimento gratuito ilimitado, resposta instantânea ou disponibilidade contínua.

## Executar o servidor no computador

Python 3.12 recomendado. No Windows, `server/START-WINDOWS.bat` cria um ambiente virtual, instala dependências e inicia o serviço. Esse iniciador ainda não foi executado em Windows nesta entrega.

Manualmente, na pasta `server`:

```bash
python -m venv .venv
```

Ative o ambiente virtual de acordo com o sistema e instale:

```bash
python -m pip install --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu -r requirements-model.txt
```

Linux/macOS:

```bash
MODEL_ENABLED=1 MODEL_DIR=./models MODEL_THREADS=2 python -m uvicorn app:app --host 127.0.0.1 --port 7860 --workers 1 --no-access-log
```

O status fica em `http://127.0.0.1:7860/health`. O primeiro início pode levar minutos, pois baixa o modelo. Os estados são `starting`, `downloading`, `loading`, `ready`, `error` ou `disabled`. Se a instalação não encontrar uma wheel compatível, a compilação do motor exige ferramentas C/C++; o Dockerfile oferece essa alternativa. Sem `MODEL_ENABLED=1`, o serviço pode pesquisar e devolver trechos, mas não sintetiza respostas.

**Docker:** na pasta principal:

```bash
docker compose up --build
```

O Dockerfile foi preparado, mas sua imagem não foi construída neste ambiente. O servidor Python foi executado diretamente e testado com o modelo real.

## Colocar na nuvem

Use uma máquina com pelo menos 4 GB de RAM, espaço para modelo/dependências e acesso HTTPS de saída. Um volume persistente evita baixar o modelo novamente a cada reinício. Publique a porta interna atrás de HTTPS e mantenha um processo de inferência por modelo. Os limites atuais destinam-se a testes de baixa concorrência.

Nenhuma hospedagem paga foi ativada. Software aberto e ausência de cobrança por chamada não tornam o servidor gratuito: a hospedagem precisa ser definida. Em 17/10/2026, a documentação do Hugging Face informa que criar Spaces Docker ou Gradio de computação exige plano pago, com uma exceção específica para até dois Gradio Spaces ZeroGPU em contas pessoais gratuitas elegíveis. Este projeto Docker não é essa exceção. Não conte com hospedagem Docker gratuita nesse serviço sem verificar a sua conta.

Fonte: https://huggingface.co/docs/hub/spaces-overview

Para testar sem contratar hospedagem, o servidor pode rodar no notebook já disponível. Para acesso externo, ele precisa de um endereço HTTPS publicado por uma solução apropriada, e o computador deve permanecer ligado. Isso é uma alternativa de teste em computador próprio, não uma nuvem gratuita permanente. Nenhum túnel público foi aberto nesta entrega.

## Cliente Android

O APK 0.4 é de teste, assinado com chave de depuração, e exige Android 8 ou superior. Ainda não foi instalado em um aparelho real nem validado visualmente.

No APK de teste, toque em **Servidor**, informe o endereço HTTPS da implantação e salve. O botão Verificar consulta `/health`. Esse campo serve para a equipe de teste.

Na versão distribuída, incorpore o endereço na compilação:

```bash
./gradlew :app:assembleDebug -PORION_BACKEND_URL=https://seu-servidor
```

No Windows, use `gradlew.bat`. Assim, as pessoas que instalarem não precisarão configurar o servidor, procurar modelos ou criar uma conta no Hugging Face. Antes de distribuição pública, gerar uma versão release assinada com chave própria. Não foi criada uma chave de publicação nesta entrega.

Para compilar: JDK 17, Android SDK 35 e Gradle Wrapper 8.9 incluído. O projeto é Kotlin puro; não exige NDK nem CMake. O Android Gradle Plugin também pode instalar Build Tools 34. Não foram incluídos caminhos específicos da máquina no pacote de código-fonte.

## Privacidade e limites

A pergunta e até duas mensagens recentes vão para o servidor configurado. O buscador e os sites consultados recebem conexões da máquina que hospeda o servidor. Não há banco de conversas nem telemetria própria. O cache temporário guarda trechos sob chave derivada da pergunta e pode conter informações presentes nela. A hospedagem pode manter seus próprios registros. O comando fornecido desliga logs de acesso do Uvicorn.

O endpoint de chat exige uma sessão validada com Google. Os limites não são uma solução completa contra abuso em larga escala. Não envie documentos privados ou credenciais ao protótipo. Configurar apenas um servidor de confiança. O cliente não contém chaves de API. Credenciais expostas nos arquivos antigos não foram usadas e ainda precisam ser revogadas no serviço de origem.

O botão Parar encerra a espera no celular; o servidor pode terminar a inferência já iniciada. O histórico some ao limpar, fechar ou recriar a atividade. Sem conexão, este cliente em nuvem não responde. A base local anterior permanece uma alternativa separada; não foi incorporada como fallback automático nesta versão.

## Validação

Consulte `TESTES.md` para os resultados e o que ainda falta validar. O teste de servidor e a compilação do APK não equivalem a uma publicação em nuvem nem a um teste real do aplicativo no celular.