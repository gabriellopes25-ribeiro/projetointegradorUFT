"""
Pacote de Microsserviços de API do SITRIB (SEFIN Palmas / UFT).

Cada subpasta dentro de `src/apis/` constitui um microsserviço independente com seu
próprio `router.py` e `Dockerfile`, registrado em `src/repositories/endpoints_registry.py`:
  - `src/apis/auth_api`                 (Autenticação, RBAC, Login Único Gov.br)
  - `src/apis/tributario_api`           (Dossiê CPF/CCI, Fila Max-Heap, Simulador)
  - `src/apis/transparencia_coleta_api` (Coleta Prefeitura 182k+, Auditoria Paginada, ETL)
  - `src/apis/ia_predicao_api`          (Machine Learning Random Forest, Score Recuperabilidade)
"""
