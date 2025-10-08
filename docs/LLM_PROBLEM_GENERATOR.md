# Gerador de Problemas PDDL via LLM

Este documento especifica como uma LLM (Large Language Model) pode gerar arquivos de problema PDDL a partir de descrições em linguagem natural, mantendo compatibilidade com o domínio hospitalar existente.

## 🎯 Objetivo

Permitir que uma LLM gere problemas PDDL válidos baseados em descrições em linguagem natural, sem modificar o domínio existente (`domains/hospital_robot.pddl`).

## 📋 Formato do Problema PDDL

### Estrutura Obrigatória

```pddl
(define (problem <nome_do_problema>)
  (:domain hospital_robot)
  
  (:objects
    <lista_de_objetos>
  )
  
  (:init
    <estado_inicial>
  )
  
  (:goal
    <objetivo>
  )
)
```

### Especificações Detalhadas

#### 1. **Cabeçalho do Problema**
```pddl
(define (problem hospital_<numero>)
  (:domain hospital_robot)
```
- **nome_do_problema**: `hospital_<numero>` (ex: `hospital_03`, `hospital_04`)
- **domínio**: Sempre `hospital_robot` (não modificar)

#### 2. **Seção :objects**
```pddl
(:objects
  <robo> - robo
  <local1> <local2> ... <localN> - local
)
```

**Regras:**
- **Robô**: Sempre `r1` (padrão do domínio)
- **Locais**: Lista de locais disponíveis no hospital
- **Tipos**: `robo` e `local` (conforme domínio)

#### 3. **Seção :init (Estado Inicial)**
```pddl
(:init
  (em r1 <local_inicial>)
  (conectado <local1> <local2>)
  (conectado <local2> <local1>)
  ; ... mais conexões
)
```

**Regras:**
- **Posição inicial**: `(em r1 <local_inicial>)`
- **Conexões**: Sempre bidirecionais `(conectado A B)` e `(conectado B A)`
- **Grafo conexo**: Todos os locais devem estar conectados

#### 4. **Seção :goal (Objetivo)**
```pddl
(:goal
  (em r1 <local_objetivo>)
)
```

**Regras:**
- **Objetivo**: Sempre `(em r1 <local_objetivo>)`
- **Formato**: Posição final desejada do robô

## 🏥 Locais Disponíveis no Hospital

### Locais Principais
- `base` - Base do robô
- `recepcao` - Recepção
- `farmacia` - Farmácia
- `sala_cirurgia` - Sala de cirurgia

### Corredores
- `corredor_central` - Corredor central
- `corredor_ala_1` - Corredor ala 1
- `corredor_ala_2` - Corredor ala 2
- `corredor_ala_3` - Corredor ala 3

### Quartos
- `quarto_101` - Quarto 101
- `quarto_102` - Quarto 102
- `quarto_103` - Quarto 103

## 📝 Exemplos de Geração

### Exemplo 1: Problema Simples
**Entrada (Linguagem Natural):**
> "O robô está na base e precisa ir para a farmácia"

**Saída PDDL:**
```pddl
(define (problem hospital_03)
  (:domain hospital_robot)
  
  (:objects
    r1 - robo
    base farmacia - local
  )
  
  (:init
    (em r1 base)
    (conectado base farmacia)
    (conectado farmacia base)
  )
  
  (:goal
    (em r1 farmacia)
  )
)
```

### Exemplo 2: Problema Complexo
**Entrada (Linguagem Natural):**
> "O robô está na recepção e precisa ir para o quarto 101, passando pelo corredor central"

**Saída PDDL:**
```pddl
(define (problem hospital_04)
  (:domain hospital_robot)
  
  (:objects
    r1 - robo
    recepcao corredor_central quarto_101 - local
  )
  
  (:init
    (em r1 recepcao)
    (conectado recepcao corredor_central)
    (conectado corredor_central recepcao)
    (conectado corredor_central quarto_101)
    (conectado quarto_101 corredor_central)
  )
  
  (:goal
    (em r1 quarto_101)
  )
)
```

## 🤖 Instruções para LLM

### Prompt Base
```
Você é um gerador de problemas PDDL para navegação hospitalar. 

DOMÍNIO: Use sempre o domínio "hospital_robot" (não modifique).

OBJETIVO: Gere um problema PDDL válido baseado na descrição fornecida.

REGRAS:
1. Nome do problema: hospital_<numero>
2. Robô: sempre "r1"
3. Tipos: "robo" e "local"
4. Conexões: sempre bidirecionais
5. Grafo: deve ser conexo (caminho entre todos os locais)
6. Objetivo: sempre (em r1 <local_objetivo>)

LOCAIS DISPONÍVEIS:
- base, recepcao, farmacia, sala_cirurgia
- corredor_central, corredor_ala_1, corredor_ala_2, corredor_ala_3
- quarto_101, quarto_102, quarto_103

FORMATO DE SAÍDA:
```pddl
(define (problem hospital_<numero>)
  (:domain hospital_robot)
  
  (:objects
    r1 - robo
    <locais_necessarios> - local
  )
  
  (:init
    (em r1 <local_inicial>)
    <conexoes_bidirecionais>
  )
  
  (:goal
    (em r1 <local_objetivo>)
  )
)
```

DESCRIÇÃO: <descrição_do_usuário>
```

### Exemplo de Uso
```
DESCRIÇÃO: O robô está na base e precisa ir para a sala de cirurgia, passando pela recepção e corredor central.
```

## ✅ Validação

### Checklist para LLM
- [ ] Nome do problema: `hospital_<numero>`
- [ ] Domínio: `hospital_robot`
- [ ] Robô: `r1 - robo`
- [ ] Locais: lista com `- local`
- [ ] Estado inicial: `(em r1 <local_inicial>)`
- [ ] Conexões: bidirecionais
- [ ] Grafo: conexo (caminho entre todos os locais)
- [ ] Objetivo: `(em r1 <local_objetivo>)`
- [ ] Sintaxe: parênteses balanceados
- [ ] Formato: PDDL válido

### Teste de Validação
```bash
# Testar problema gerado
python planner.py fast-downward hospital <numero>
python planner.py mock hospital <numero>
```

## 🚫 Limitações

### O que NÃO fazer:
- ❌ Modificar o domínio existente
- ❌ Adicionar novos tipos além de `robo` e `local`
- ❌ Adicionar novas ações além de `navegar`
- ❌ Usar locais não listados
- ❌ Criar grafos desconexos
- ❌ Modificar a estrutura do domínio

### O que fazer:
- ✅ Usar apenas locais listados
- ✅ Manter conexões bidirecionais
- ✅ Garantir grafo conexo
- ✅ Seguir formato PDDL exato
- ✅ Usar sintaxe correta

## 📚 Referências

- **Domínio**: `domains/hospital_robot.pddl`
- **Problemas existentes**: `problems/hospital_01.pddl`, `problems/hospital_02.pddl`
- **Sistema**: `python planner.py <planner> hospital <numero>`
