# Estudo de Caso: Robô de Navegação Hospitalar

## 📋 Visão Geral

Este é o **caso de estudo inicial** focado exclusivamente em **navegação** de um robô autônomo em ambiente hospitalar.

### Objetivo
Permitir que um robô (tipo Pudu Robotics/Agliex) navegue entre diferentes locais de um hospital através de comandos em linguagem natural.

### Escopo Atual - v1.0
- ✅ **Navegação** entre locais
- ❌ Pegar/soltar items (futuro)
- ❌ Gestão de bateria (futuro)
- ❌ Compartimentos (futuro)

---

## 🏥 Mapa do Hospital

```
                    HOSPITAL LAYOUT
                    
                    ┌─────────────┐
                    │    Base     │ (Ponto de recarga/início)
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  Recepção   │
                    └──────┬──────┘
                           │
                ┌──────────┴──────────┐
                │  Corredor Central   │ (HUB)
                └─┬───┬───┬───┬───┬───┘
                  │   │   │   │   │
        ┌─────────┘   │   │   │   └─────────┐
        │             │   │   │             │
   ┌────┴────┐   ┌────┴┐ │ ┌─┴────┐   ┌────┴────┐
   │Farmácia │   │ Lab │ │ │Cirur.│   │Corredor │
   └─────────┘   └─────┘ │ └──────┘   │  Ala 1  │
                         │             └─────────┘
                    ┌────┴────┐
                    │Corredor │
                    │  Ala 2  │
                    └─┬──┬──┬─┘
                      │  │  │
                   ┌──┴┐ │ ┌┴───┐
                   │201│ │ │205 │
                   └───┘ │ └────┘
                      ┌──┴───┐
                      │ 202  │
                      └──────┘
```

---

## 📂 Arquivos do Estudo de Caso

### Domain: `domains/hospital_robot.pddl`

**Define o que o robô PODE fazer:**
- **Tipos:** `robot`, `location`
- **Predicados:** `at`, `connected`
- **Ação:** `navigate`

### Problems: `problems/hospital_*.pddl`

**Definem cenários específicos:**

| Arquivo | Descrição | Comando Exemplo |
|---------|-----------|-----------------|
| `hospital_01.pddl` | Navegação simples (2 locais) | "Vá para a farmácia" |
| `hospital_02_multiplos_locais.pddl` | Caminho com etapas intermediárias | "Vá até o quarto 205" |
| `hospital_03_rota_complexa.pddl` | Rota longa (5+ locais) | "Vá até o laboratório" |
| `hospital_04_ida_e_volta.pddl` | Missão com retorno | "Vá à farmácia e volte" |
| `hospital_05_mapa_completo.pddl` | Hospital completo | "Vá até o quarto 305" |

---

## 🚀 Como Executar

### Pré-requisitos
- Fast-Downward instalado
- Python 3.x

### Método 1: Script Automático

**Windows:**
```powershell
.\examples\testar_planejador.bat
```

**Linux/Mac:**
```bash
chmod +x examples/testar_planejador.sh
./examples/testar_planejador.sh
```

### Método 2: Linha de Comando Direta

**Estrutura básica:**
```bash
fast-downward.py <domain.pddl> <problem.pddl> --search "<algoritmo>"
```

**Exemplo Windows:**
```powershell
cmd /c "python fast-downward.py domains/hospital_robot.pddl problems/hospital_01.pddl --search astar(blind())"
```

**Exemplo Linux/Mac:**
```bash
./fast-downward/fast-downward.py \
  domains/hospital_robot.pddl \
  problems/hospital_01.pddl \
  --search "astar(blind())"
```

### Algoritmos de Busca Recomendados

| Algoritmo | Uso | Comando |
|-----------|-----|---------|
| `astar(blind())` | Mais rápido, simples | `--search "astar(blind())"` |
| `astar(lmcut())` | Ótimo, pode ser lento | `--search "astar(lmcut())"` |
| `lazy_greedy([ff()])` | Muito rápido | `--search "lazy_greedy([ff()])"` |

---

## 📝 Exemplos de Conversão

### Exemplo 1: Navegação Simples

**Comando em Linguagem Natural:**
> "Robô, vá para a farmácia"

**Análise:**
- **Robô:** robo
- **Destino:** farmacia
- **Origem:** base (assumida)

**Problem.pddl gerado:**
```pddl
(define (problem hospital-ir-farmacia)
  (:domain hospital-robot-simple)
  
  (:objects
    robo - robot
    base farmacia - location
  )
  
  (:init
    (at robo base)
    (connected base farmacia)
    (connected farmacia base)
  )
  
  (:goal
    (at robo farmacia)
  )
)
```

**Plano esperado:**
```
navigate robo base farmacia
```

---

### Exemplo 2: Caminho com Etapas

**Comando:**
> "Robô, vá até o quarto 205"

**Contexto:** Robô precisa passar pelo corredor

**Problem.pddl:**
```pddl
(define (problem hospital-ir-quarto-205)
  (:domain hospital-robot-simple)
  
  (:objects
    robo - robot
    base corredor_ala_2 quarto_205 - location
  )
  
  (:init
    (at robo base)
    (connected base corredor_ala_2)
    (connected corredor_ala_2 base)
    (connected corredor_ala_2 quarto_205)
    (connected quarto_205 corredor_ala_2)
  )
  
  (:goal
    (at robo quarto_205)
  )
)
```

**Plano esperado:**
```
navigate robo base corredor_ala_2
navigate robo corredor_ala_2 quarto_205
```

---

### Exemplo 3: Ida e Volta

**Comando:**
> "Vá à farmácia e retorne para a base"

**Problem.pddl:**
```pddl
(define (problem hospital-farmacia-e-retorno)
  (:domain hospital-robot-simple)
  
  (:objects
    robo - robot
    base farmacia corredor - location
  )
  
  (:init
    (at robo base)
    (connected base corredor)
    (connected corredor base)
    (connected corredor farmacia)
    (connected farmacia corredor)
  )
  
  (:goal
    (at robo base)  ; Retornar à base
  )
)
```

**Plano esperado:**
```
; Nota: se o goal é apenas estar na base, 
; e o robô já está na base, o plano será VAZIO
; Para forçar ida e volta, precisaríamos de predicados adicionais
```

---

## 🤖 Papel da IA Planejadora

### Input (Linguagem Natural)
```
"Robô, vá até o laboratório"
```

### Processo Mental da IA

1. **Identificar entidades:**
   - Destino: `laboratorio`
   - Robô: `robo` (padrão)
   - Origem: `base` (assumido se não especificado)

2. **Consultar mapa do hospital:**
   - Caminho: base → recepcao → corredor_central → corredor_ala_1 → laboratorio

3. **Gerar conectividade necessária:**
   ```pddl
   (connected base recepcao)
   (connected recepcao corredor_central)
   (connected corredor_central corredor_ala_1)
   (connected corredor_ala_1 laboratorio)
   ; + conexões bidirecionais (volta)
   ```

4. **Montar problem.pddl:**
   - Objects: robô + todos os locais
   - Init: posição inicial + todas as conexões
   - Goal: `(at robo laboratorio)`

### Output (Problem.pddl)
```pddl
(define (problem hospital-ir-laboratorio)
  (:domain hospital-robot-simple)
  (:objects
    robo - robot
    base recepcao corredor_central corredor_ala_1 laboratorio - location
  )
  (:init
    (at robo base)
    (connected base recepcao)
    (connected recepcao base)
    (connected recepcao corredor_central)
    (connected corredor_central recepcao)
    (connected corredor_central corredor_ala_1)
    (connected corredor_ala_1 corredor_central)
    (connected corredor_ala_1 laboratorio)
    (connected laboratorio corredor_ala_1)
  )
  (:goal (at robo laboratorio))
)
```

---

## 🔍 Validação e Debug

### Checklist antes de executar:

- [ ] Domain existe: `domains/hospital_robot.pddl`
- [ ] Problem existe e está completo
- [ ] Todos os locais mencionados estão em `:objects`
- [ ] Conectividade está bidirecional (se necessário)
- [ ] Robô tem posição inicial
- [ ] Goal está correto

### Erros Comuns

#### 1. "No solution found"
**Causa:** Caminho impossível

**Solução:**
- Verificar se todas as conexões necessárias existem
- Verificar se não falta `(connected A B)` E `(connected B A)`

**Exemplo:**
```pddl
; ERRADO - falta volta
(connected base farmacia)

; CERTO - bidirecional
(connected base farmacia)
(connected farmacia base)
```

#### 2. "Unknown predicate"
**Causa:** Predicado não existe no domain

**Solução:**
- Usar apenas: `at`, `connected`

#### 3. "Type mismatch"
**Causa:** Objeto com tipo errado

**Solução:**
- Usar apenas tipos: `robot`, `location`

---

## 📊 Métricas dos Exemplos

| Problem | Locais | Conexões | Passos Esperados |
|---------|--------|----------|------------------|
| hospital_01 | 2 | 2 | 1 |
| hospital_02 | 3 | 4 | 2 |
| hospital_03 | 5 | 8 | 4 |
| hospital_04 | 3 | 4 | ~2-4 |
| hospital_05 | 15+ | 30+ | 3-5 |

---

## 🎯 Prompt para IA Planejadora

Use este prompt ao configurar uma IA:

```
Você é uma IA Planejadora PDDL especializada em robôs hospitalares.

SEU TRABALHO:
1. Receber comandos em linguagem natural
2. Gerar arquivos problem.pddl válidos
3. Usar o domain: hospital-robot-simple

DOMAIN DISPONÍVEL:
- Tipos: robot, location
- Predicados: (at ?r - robot ?loc - location), (connected ?from ?to - location)
- Ação: navigate

MAPA DO HOSPITAL:
[Consulte docs/HOSPITAL_CASE_STUDY.md]

REGRAS:
- Sempre incluir conectividade bidirecional
- Robô começa na 'base' se não especificado
- Normalizar nomes: "quarto 205" → quarto_205

EXEMPLO:
Input: "Vá para o quarto 205"
Output: [problem.pddl com caminho base → corredor_ala_2 → quarto_205]
```

---

## 📈 Próximas Versões

### v2.0 - Transporte de Items
- Adicionar tipo: `item`
- Adicionar ações: `pick`, `drop`
- Casos: "Leve medicamento para quarto 205"

### v3.0 - Bateria
- Adicionar predicado: `battery-level`
- Adicionar ação: `charge`
- Casos: "Vá ao quarto 305, mas recarregue se necessário"

### v4.0 - Multi-compartimento
- Adicionar tipo: `compartment`
- Múltiplos items simultâneos

---

## 📞 Suporte

**Problemas com Fast-Downward?**
- Consulte: `docs/QUICK_START.md`

**Dúvidas sobre PDDL?**
- Consulte: `docs/AI_PLANNER_ROLE.md`

**Exemplos complexos?**
- Consulte: `docs/EXAMPLES.md`

---

**Última atualização:** Outubro 2025  
**Versão:** 1.0 - Navegação Básica

