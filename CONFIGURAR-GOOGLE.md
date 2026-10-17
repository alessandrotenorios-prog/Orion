# Ativar o login Google — ORION 0.4

O código do login foi implementado. **Este APK não contém um servidor ativo nem um projeto Google já autorizado.** Sem essas configurações, é possível abrir a interface e verificar a indicação de conexão pendente; não é possível completar o login nem conversar com a IA.

Não é necessário fornecer a senha do Gmail ao ORION. O login usa a tela oficial de contas do Google, via Credential Manager. O servidor valida o ID token com a biblioteca Google Auth; não confia em um e-mail digitado no aplicativo.

## Configuração do responsável pelo aplicativo

1. Acesse o Google Cloud Console com sua conta Google existente e crie ou selecione um projeto.
2. Configure a Google Auth Platform (marca, público e informações básicas de contato). Se estiver no modo de testes, adicione o Gmail que usará no teste à lista de usuários permitidos.
3. Crie um cliente OAuth **Android** com pacote `br.com.orion.cloud` e o SHA-1 do certificado deste APK de teste:

```text
20:1C:54:6D:68:F2:EC:09:D2:0C:95:39:17:B8:1C:09:4D:09:95:30
```

4. No mesmo projeto, crie um cliente OAuth do tipo **Aplicativo da Web**. Ele fornece o ID do cliente que termina em `.apps.googleusercontent.com`.
5. No servidor, defina a variável `GOOGLE_WEB_CLIENT_ID` com esse ID público. Não coloque um client secret no aplicativo. Esta implementação não precisa de um client secret.
6. Publique o servidor com HTTPS e reinicie-o após definir a variável. `/health` mostrará `google_configured: true`. Não é necessário expor o modelo no celular.
7. No APK, em Servidor, informe o endereço HTTPS da implantação. Toque em **Entrar com Google**, escolha a conta na tela oficial e envie uma pergunta após o servidor validar o login.

Exemplo Linux (na pasta `server`, com dependências instaladas):

```bash
GOOGLE_WEB_CLIENT_ID=seu-id.apps.googleusercontent.com MODEL_ENABLED=1 MODEL_DIR=./models python -m uvicorn app:app --host 127.0.0.1 --port 7860 --workers 1 --no-access-log
```

Em Docker Compose, inclua `GOOGLE_WEB_CLIENT_ID` no ambiente do serviço. O host/proxy deve publicar HTTPS. Na distribuição final, compile com `-PORION_BACKEND_URL=https://seu-servidor` para que os usuários não precisem inserir endereço.

O APK de teste usa uma assinatura de depuração. Uma nova assinatura ou a chave de produção exige registrar o SHA-1 correspondente no cliente Android. O certificado de depuração não substitui uma chave de publicação própria.

## Funcionamento e privacidade

- O servidor cria uma tentativa de login com nonce, válida por cinco minutos.
- O Google emite a credencial para o cliente configurado. O servidor verifica assinatura, emissor, audiência e validade com Google Auth, e compara o nonce com a tentativa pendente.
- Após validar, cria uma sessão aleatória do ORION, guardada apenas em memória, válida por no máximo uma hora e nunca além da validade do token Google.
- O chat exige a sessão; apenas colocar um e-mail ou um Bearer inventado não libera acesso.
- A sessão não é salva em preferências do Android. Ao fechar/recriar o aplicativo ou reiniciar o servidor, poderá ser necessário entrar novamente.
- Sair tenta invalidar a sessão no servidor e sempre limpa a sessão e o histórico local. Se não houver conexão, a sessão remota pode permanecer até expirar.
- O app recebe nome e e-mail básicos; não solicita acesso a mensagens do Gmail, contatos ou arquivos do Google Drive.
- O login identifica o usuário. Ele não fornece hospedagem, não ativa Cloud Run e não torna a inferência gratuita.

Nenhuma conta Google, hospedagem, configuração OAuth ou cobrança foi criada em nome do usuário nesta entrega.

## Testes desta versão

30 testes automatizados passaram no servidor. Os testes de fluxo de login usam um verificador Google substituído por um objeto de teste para checar nonce, audiência solicitada, sessão, expiração e saída. Isso **não é um teste real de login com o Google**. O verificador de produção chama a biblioteca oficial; o fluxo com uma conta real ainda depende do projeto configurado e do aparelho.

Fontes oficiais consultadas:

- https://developer.android.com/identity/sign-in/credential-manager-siwg
- https://developers.google.com/identity/sign-in/android/backend-auth
