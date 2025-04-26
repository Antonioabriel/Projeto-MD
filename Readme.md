# **Tutotial Github**

## **Criar um projeto novo**
  
  - Criar uma nova pasta no PC pra isso chamada ```Projeto-MD```
  
  - Abrir o VSCode nessa pasta
  
  - Criar um novo arquivo ```README.md```
  
  - Escrever dentro dele o que for preciso para a ```compreenção``` do codigo
  
  - Salva o arquivo

## **Agora então é hora de usarmos o Git**

- Abre o Git Bash que foi instalado na máquina (pode ser pelo terminal do VSCode mesmo)

- ```git init``` para inicializar o repositório

- Foi criada uma pasta ```.git``` e é ali que toda a mágica acontece, então não apague

- git add ```README.md``` para colocar o arquivo na área de stagging

  ![image](https://github.com/user-attachments/assets/6d6997ad-3e81-4e13-a179-9cbe12f30b22)

  Esse `add` é necessário antes de darmos o commit para adicionar as pastas

* `git commit -m "primeiro commit"` para de fato dar o commit no repositório

* `git branch -M "main"` para alterar o nome da branch principal de `master` para `main` (isso é uma boa prática atualmente recomendada)



## Repositório no Github

* Depois de você ter criado a sua conta na plataforma, você irá em `Criar novo repositório`

Você vai preencher com as informações do projeto, então dar o nome do repositório, colocar uma breve descrição e criar

Copie o link que aparecer para você `https://github.com/Antonioabriel/Projeto-MD.git`


* Para passar o commit do meu repositório local (da minha máquina) para um repositório na plataforma do Github, usamos o `git remote add origin <link do repositório>`

* `origin` é o nome utilizado para referenciar o nosso repositório

Agora já temos o nosso repositório local conectado com o respositório do Github, porém o `commit` que damos na máquina não sobe automaticamente para a plataforma

* Para isso precisaremos empurrar, enviar para lá com o `git push -u origin main`

Agora se recarregarmos a página iremos ver o nosso arquivo aqui na plataforma!

## Alterando e adicionando arquivo

Primeira coisa que faremos então é alterar esse arquivo que já commitamos

* Adiciona mais uma frase no arquivo `Essa é uma alteração`

* Além disso iremos criar um novo arquivo `Projeto.md`, onde escreveremos `Esse é o arquivo onde desenvolverei o meu projeto`

* Agora então precisamos subir essa alteração, pra isso seguiremos os mesmos passos de `git add .` (agora ponto `.` pois adiciona todos os arquivos) e `git commit -m "Primeira alteração"`

* Lembrando que para alterar algo no nosso respositório do Github precisamos dar o push, então `git push origin main` (sem o -u)

Se olharmos agora o nosso código no Github, ele terá sido alterado, e não só isso, se clicarmos no nome do `commit`, podemos ver exatamente as alterações que foram feitas nele.
O verde com `+` e o vermelho com `-` mostra, os conteúdos que foram adicionados e editados dentro do código.
Aqui nesse botão poderemos ver todos os commits já feitos anteriormente, então se clicarmos em algum deles, veremos exatamente o que havia sido alterado, além de claro, vermos o código como era.



## Branch

Até agora tudo o que fizemos de alterações e mandamos de commit, foi na nossa `main`, que é aquela linha do tempo principal.
Agora vamos criar uma branch e depois juntamos ela com o código que já está na `main` (lembrando que ela é uma linha cronológica adicional/alternativa a principal)
E outra, a branch pode ser criada tanto para quando você for fazer uma alteração em um arquivo, quando para adicionar outro arquivo dentro do projeto ou mesmo excluir.
<br>


* Nesse caso vamos adicionar um novo arquivo para desenvolver a nossa feature `Botão`

* Então a primeira coisa que fazemos é `git checkout -b "novo-botao"`, assim criando uma branch para ele
Esse comando além de criar a branch já entra nela com o checkout.

* Vou então criar o arquivo, criar o `botão.md` "aqui eu crio o botão"

* E agora fazemos o passo a passo que já sabemos, colocamos a nossa alteração em stagging com o `git add .` e commitamos com o `git commit -m "novo botão"`

* Para enviarmos agora que vai ser diferente. Em vez de que utilizávamos o `git push orgin main`, usaremos `git push origin botao`

Agora se olharmos o nosso Github, veremos que tem 2 branches, a `main` e a `botao`



Vamos supor que eu ainda não tivesse terminado de desenvolver o botão, eu poderia continuar tranquilamente na branch `botao` até terminar!

Se você precisasse por algum motivo voltar naquela branch `main` e desenvolver a partir do que deixou lá, a única coisa que você precisa fazer nesse caso é `git checkout main`, e pra voltar depois é só `git checkout botao` novamente


## Merge

* Agora o que precisamos fazer é ir para a nossa branch principal `git checkout main` e lá faremos o merge com a branch `botao` que criamos, com `git merge botao`

Pronto, agora tudo o que tinha de alteração na branch `botao` juntou com a `main`

* Para finalizar então, vamos jogar lá no Github isso tudo com o `git push origin main`

## Clone



Sempre que você entrar em um repositório, seja o seu ou o de qualquer outra pessoa, terá esse botão `Code`, que quando você clica aparece um link:



* Você irá copiar esse link e levar ele lá pro terminal

* O comando para puxar o projeto para a sua máquina é o `git clone https://github.com/rafaballerini/GitTutorial.git`

Não é necessário criar um repositório antes disso, como fizemos anteriormente com o `git init`. Dessa vez, basta abrir o terminal e clonar o projeto e tudo aparecerá!

## Pull

Caso ouver alteração no repositório.

* Basta você executar o comando `git pull`, ele irá puxar todas as alterações feitas no repositório do Github para o seu repositório local

## Fork


Existe a ferramenta `fork`, que puxar o repositorio de outro usuario pro seu.


## Pull request


* Após você ter dado um fork no projeto e ele ter ido pra sua conta, você poderá alterar o projeto e adicionar as funcionalidades que deseja


* Depois disso, você poderá salvar o projeto, dar o `git add .`, `git commit -m "validação de botões"` e `git push origin main`

Quando você for olhar o seu Github, verá que existe uma mensagem parecida com a seguinte:

`this branch is 1 commit ahead of 1 commit behind main`

Isso significa que a branch do seu repositório está 1 commit "na frente" da branch original

O que você deve perceber agora é esse botão que aparece em seguida:

`Contribute`

Ele servirá para caso você deseje enviar para o dono do repositório original uma solicitação de pull, ou seja, fazer com que ele puxe as alterações que você fez no seu repositório para o repositório dele, original

Ao clicar nesse botão, você será direcionado para uma página que fará a avaliação se esse `pull request` terá conflitos ou não com o código no repositório original. Caso não tenha, bastão clicar no botão de `Create pull request`


Você irá colocar um nome intuitivo, que demonstre a funcionalidade adicionada e o ideal é que você também crie uma boa descrição do que desenvolveu, não somente explicando o que é, mas ensinando ao dono do repositório original a forma como ele poderá testar também

Depois disso, basta esperar para que o dono da branch original aceite o seu pull request

