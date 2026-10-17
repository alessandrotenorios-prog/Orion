# Atualização 0.4 — login Google

APK 0.4 compilado com sucesso; assinatura de depuração verificada e mantida igual à versão anterior. Tamanho aproximado de 4,3 MB. Não foi instalado em aparelho real.

30 testes do servidor passaram, incluindo proteção do chat, configuração Google ausente, criação e invalidação de sessão, nonce incorreto, tentativa reutilizada, rejeição de verificação de credencial e sessão expirada. O fluxo OAuth real não foi testado por ausência de projeto Google configurado. Consulte CONFIGURAR-GOOGLE.md.

Os resultados abaixo foram medidos na versão 0.3 para o mecanismo de pesquisa e modelo, preservado nesta atualização.

# Verificação da versão 0.3

Data: 17/10/2026.

## Resultados observados

- **24 testes automatizados passaram**, cobrindo os oito perfis, bloqueio de endereços privados, leitura de resultados, relevância dos trechos, filtro de número de equipamento, entrada inválida, limitação de requisições e comportamento sem modelo ou fontes.
- **Modelo real executado:** Qwen2.5-1.5B-Instruct Q4_K_M via llama-cpp-python 0.3.36, dois threads, contexto de 4.096 tokens.
- **Teste com fonte controlada:** o texto de teste informava capacidade de 20 litros e manutenção a cada 250 horas. O modelo respondeu corretamente a ambos os dados. Geração de aproximadamente 13,6 segundos. Isso verifica leitura de uma fonte artificial simples, não precisão geral.
- **Teste com pesquisa real:** busca sobre Epiroc Pit Viper 271 leu duas páginas oficiais da Epiroc, sem intervenção do usuário no navegador.
- **Teste completo da API com pesquisa e inferência reais:** a pergunta “Epiroc Pit Viper 271: qual é a faixa de diâmetro de perfuração?” retornou HTTP 200, assistente GENIUS e resposta “171 a 270 mm (6-3/4 a 10-5/8 pol)”. O resultado era sustentado pela página oficial consultada. Tempo total: aproximadamente 37,7 segundos, em uma única execução.
- **Android:** `:app:assembleDebug` concluiu com sucesso. APK com cerca de 809 KiB, pacote `br.com.orion.cloud`, versão `0.3.0-cloud-alpha`, Android 8+ (API 26), target API 35. Verificação da assinatura de depuração passou. O manifesto compilado contém apenas permissão de internet e bloqueia HTTP sem TLS.

Os tempos variam com o hardware, a conexão, o tamanho das páginas, o texto da resposta e a concorrência. Não constituem um benchmark de serviço em nuvem nem promessa de desempenho. Um teste correto não demonstra a confiabilidade de todas as respostas do modelo.

## Ainda não validado

- Instalação, teclado, layout e conversa no aparelho Android real.
- Publicação em hospedagem permanente e comunicação do APK com essa implantação.
- Imagem Docker construída e iniciador Windows executado.
- Testes de carga, alta disponibilidade, autenticação para distribuição ampla e versão release assinada.
- Resistência geral do modelo a alucinações e instruções maliciosas presentes em páginas.

A busca geral lê HTML público e pode parar de funcionar por bloqueios ou mudanças. A alternativa da Wikipédia não equivale a pesquisa geral atualizada. O servidor informa as falhas; não as transforma em confirmação de fatos.
