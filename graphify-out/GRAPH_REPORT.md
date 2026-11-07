# Graph Report - klique-api  (2026-11-07)

## Corpus Check
- 162 files · ~86,064 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: .css 16, (none) 9, .example 3)

## Summary
- 1442 nodes · 2870 edges · 112 communities (71 shown, 41 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 128 edges (avg confidence: 0.92)
- Token cost: 21,444 input · 3,149 output

## Community Hubs (Navigation)
- Billing & PIX Payments
- Billing & PIX Payments
- Apple & Native Auth
- Apple & Native Auth
- Avatar & Visual Comparisons
- Traefik Reverse Proxy & Gateway
- Internationalization & Locales
- Flashcard Review & Training UI
- Android & Mobile Pipeline
- Billing & PIX Payments
- Data Models & DTO Schemas
- Knowledge Domains Management
- Navigation & UI Atoms
- Data Models & DTO Schemas
- Android & Mobile Pipeline
- Authentication & Tokens
- Billing & PIX Payments
- WhatsApp Integration Service
- Authentication & Tokens
- Billing & PIX Payments
- Authentication & Tokens
- Data Models & DTO Schemas
- Authentication & Tokens
- Data Models & DTO Schemas
- Data Models & DTO Schemas
- Data Models & DTO Schemas
- WhatsApp Integration Service
- Authentication & Tokens
- Data Models & DTO Schemas
- Application Configuration
- Image Generation & Prompts
- Android & Mobile Pipeline
- AI Oracle & Intelligent Agents
- Data Models & DTO Schemas
- Flashcards Generation & SRS
- Data Models & DTO Schemas
- Data Models & DTO Schemas
- Setup Cookies Module
- Navigation & UI Atoms
- Application Configuration
- WhatsApp Integration Service
- Flashcards Generation & SRS
- WhatsApp Integration Service
- Docker & Container Infrastructure
- WhatsApp Integration Service
- Navigation & UI Atoms
- Data Models & DTO Schemas
- Database & MongoDB Connections
- Authentication & Tokens
- Application Configuration
- Database & MongoDB Connections
- Gpt4Free Provider Module
- Automated Test Suite
- WhatsApp Integration Service
- Docker & Container Infrastructure
- Database & MongoDB Connections
- Authentication & Tokens
- Data Models & DTO Schemas
- Billing & PIX Payments
- WhatsApp Integration Service
- Docker & Container Infrastructure
- Docker & Container Infrastructure
- Knowledge Domains Management
- WhatsApp Integration Service
- Docker & Container Infrastructure
- Android & Mobile Pipeline
- WhatsApp Integration Service
- Docker & Container Infrastructure
- Docker & Container Infrastructure
- Docker & Container Infrastructure
- Frontend Tooling & Dependencies
- Billing & PIX Payments
- Android & Mobile Pipeline
- Data Models & DTO Schemas
- Docker & Container Infrastructure
- Frontend Tooling & Dependencies
- Application Configuration
- Flashcards Generation & SRS
- Flashcards Generation & SRS
- Database & MongoDB Connections
- Image Generation & Prompts
- Image Generation & Prompts
- Image Generation & Prompts
- Image Generation & Prompts
- Pyproject Module

## God Nodes (most connected - your core abstractions)
1. `WhatsAppService` - 56 edges
2. `react` - 45 edges
3. `react-i18next` - 42 edges
4. `useAuth()` - 36 edges
5. `environment` - 31 edges
6. `get_db()` - 25 edges
7. `environment` - 25 edges
8. `get_current_active_user()` - 21 edges
9. `react-router-dom` - 21 edges
10. `IconSparkBoost()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `test_status_deletion_detailed()` --uses--> `WhatsAppService`  [INFERRED]
  tests/test_status_deletion.py → app/services/whatsapp.py
- `test_delete_nonexistent_status()` --uses--> `WhatsAppService`  [INFERRED]
  tests/test_status_deletion.py → app/services/whatsapp.py
- `test_status_existence_check()` --uses--> `WhatsAppService`  [INFERRED]
  tests/test_status_deletion.py → app/services/whatsapp.py
- `create_admin_interactive()` --calls--> `get_password_hash()`  [EXTRACTED]
  scripts/create_admin.py → app/dependencies.py
- `test_generate_and_save_image_uses_generated_image_save()` --calls--> `generate_and_save_image()`  [EXTRACTED]
  tests/test_image_generation_service.py → app/services/image_generation.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Internal Economy & PIX Payments Pipeline** ? app_routers_payments_create_pix_payment, app_routers_payments_get_payment_status, app_routers_payments_mercadopago_webhook, app_services_mercadopago_mercadopagoservice, app_routers_credits_use_one_credit, app_routers_credits_add_paid_credits, frontend_src_components_payment_buycredits_jsx [INFERRED 0.98]
- **SRS Spaced Repetition (SM-2) & Gamification Pipeline** ? app_routers_srs_apply_sm2, app_routers_srs_submit_review, app_routers_srs_get_due_cards, app_routers_srs_get_srs_stats, frontend_src_pages_trainingpage_jsx, frontend_src_pages_cardswipepage_jsx, frontend_src_services_api_js [INFERRED 0.98]
- **AI Cognitive & Visual Synthesis Pipeline** ? app_agents_agent_agentcache, app_agents_tasks_process_message_with_agent, app_services_image_generation_generate_and_save_image, app_services_image_generation_build_card_image_prompt, app_agents_omniflash_oracle_prompt, app_routers_cards_cards_py [INFERRED 0.98]
- **WhatsApp Cross-Boundary Service Bridge** ? app_services_whatsapp_whatsappservice, app_routers_auth_auth_py, app_routers_whatsapp_process_status_viewed_for_image_generation, app_services_image_generation_image_generation_py, app_services_shared_shared_py [INFERRED 0.98]
- **AI Agent Ecosystem** — app_agents_concurso_ce_prompt, app_agents_concurso_me_prompt, app_agents_omniflash_oracle_prompt, app_agents_pocket_oracle_prompt, app_agents_prompts_instagram_post, app_agents_prompts_linkedin_post, app_agents_prompts_whatsapp_status [EXTRACTED 1.00]
- **Social Media Automation Flow** — app_scheduler, app_agents_tasks, app_agents_prompts_instagram_post, app_agents_prompts_linkedin_post, app_agents_prompts_whatsapp_status [EXTRACTED 0.95]

## Communities (112 total, 41 thin omitted)

### Community 0 - "Billing & PIX Payments"
Cohesion: 0.08
Nodes (17): get_payment_transactions_collection(), get_user_credits_collection(), get_current_active_user(), read_users_me(), add_paid_credits(), check_user_has_credits(), get_credits_balance(), get_credits_history() (+9 more)

### Community 1 - "Billing & PIX Payments"
Cohesion: 0.07
Nodes (34): AppleLoginRequest, ChangePasswordRequest, CreatePixPaymentRequest, CreatePixPaymentResponse, CreditHistoryItem, CreditHistoryResponse, DueCard, GoogleLoginRequest (+26 more)

### Community 2 - "Apple & Native Auth"
Cohesion: 0.13
Nodes (34): AppleLoginButton(), NativeAppleLoginButton(), WebAppleLoginButton(), GoogleLoginButton(), NativeGoogleLoginButton(), WebGoogleLoginButton(), LoginForm(), RegisterForm() (+26 more)

### Community 3 - "Apple & Native Auth"
Cohesion: 0.09
Nodes (27): authenticate_token(), create_access_token(), invalidate_token(), verify_password(), apple_login(), change_email(), change_password(), confirm_change_email() (+19 more)

### Community 4 - "Avatar & Visual Comparisons"
Cohesion: 0.12
Nodes (29): AvatarGenerator(), ImageComparator(), defaultProps, IconCameraShot(), IconCheckShield(), IconCopyRunes(), IconCutBlade(), IconDownloadDrop() (+21 more)

### Community 5 - "Traefik Reverse Proxy & Gateway"
Cohesion: 0.05
Nodes (38): accessLog, filters, format, email, httpChallenge, storage, api, dashboard (+30 more)

### Community 6 - "Internationalization & Locales"
Cohesion: 0.07
Nodes (30): files, findFiles(), fs, path, findFiles(), fs, path, androidResPath (+22 more)

### Community 7 - "Flashcard Review & Training UI"
Cohesion: 0.12
Nodes (25): TrainingPage, CardEditModal(), heatColor(), inputStyle, labelStyle, TEMPLATES, ConcursoCard(), DeckPileDisplay() (+17 more)

### Community 8 - "Android & Mobile Pipeline"
Cohesion: 0.06
Nodes (33): runs-on, steps, timeout-minutes, VITE_API_URL, jobs, build-android, name, on (+25 more)

### Community 9 - "Billing & PIX Payments"
Cohesion: 0.06
Nodes (31): APPLE_CLIENT_ID, CREDITS_PER_REAL, DB_CONNECTION, DB_DATABASE, DB_HOST, DB_PASSWORD, DB_PORT, DB_USERNAME (+23 more)

### Community 10 - "Data Models & DTO Schemas"
Cohesion: 0.11
Nodes (11): upload_card_image(), create_domain(), delete_domain(), improve_domain_image(), regenerate_domain_image(), remove_domain_image(), update_domain(), upload_domain_image() (+3 more)

### Community 11 - "Knowledge Domains Management"
Cohesion: 0.12
Nodes (22): DomainSVGCard(), getTheme(), THEME_MAP, DomainEditModal(), inputStyle, labelStyle, THEMES, IconDelete() (+14 more)

### Community 12 - "Navigation & UI Atoms"
Cohesion: 0.13
Nodes (21): IconClose(), IconDeckCard(), IconPhoto(), IconStrategy(), NAV_LINKS_KEYS, Navbar(), ThemeSettingsModal(), EntityCard() (+13 more)

### Community 13 - "Data Models & DTO Schemas"
Cohesion: 0.12
Nodes (15): get_scenario_cards_collection(), _card_generation_stream(), generate_card_stream(), stream_generator(), generate_sse_event(), improve_card_image(), _load_prompt(), regenerate_card_image() (+7 more)

### Community 14 - "Android & Mobile Pipeline"
Cohesion: 0.15
Nodes (14): add_android_platform_if_missing(), build_frontend(), clear_gradle_cache(), ensure_npm_dependencies(), execute_gradle(), fix_duplicate_resources(), install_typescript_optional(), _load_domain() (+6 more)

### Community 15 - "Authentication & Tokens"
Cohesion: 0.14
Nodes (21): App(), AppRoutes(), AppShell(), CardSwipePage, DashboardPage, DomainsPage, DynamicStatusBarHandler(), LoginPage (+13 more)

### Community 16 - "Billing & PIX Payments"
Cohesion: 0.08
Nodes (25): CREDITS_PER_REAL, DB_CONNECTION, DB_DATABASE, DB_HOST, DB_PASSWORD, DB_PORT, DB_USERNAME, FREE_CREDITS_PER_USER (+17 more)

### Community 18 - "Authentication & Tokens"
Cohesion: 0.16
Nodes (15): get_cache_collection(), get_db(), get_link_analytics_collection(), get_magic_links_collection(), get_mail_confirmation_collection(), get_otp_collection(), get_password_recovery_collection(), get_processed_messages_collection() (+7 more)

### Community 19 - "Billing & PIX Payments"
Cohesion: 0.11
Nodes (4): authenticate_user(), get_current_user(), get_current_user_optional(), get_token_from_header()

### Community 20 - "Authentication & Tokens"
Cohesion: 0.17
Nodes (15): get_password_hash(), check_account(), confirm_code(), register(), send_confirmation_code(), _send_email(), verify_email(), confirmCodeRequest (+7 more)

### Community 21 - "Data Models & DTO Schemas"
Cohesion: 0.13
Nodes (12): MongoBaseModel, Review, ReviewSubmitRequest, ReviewSubmitResponse, ScenarioCard, SimulationLog, SRSStats, _apply_sm2() (+4 more)

### Community 22 - "Authentication & Tokens"
Cohesion: 0.09
Nodes (22): dependencies, axios@^1.13.2, @capacitor/android@^6.0.0, @capacitor-community/apple-sign-in@^6.0.0, @capacitor/core@^6.0.0, chart.js@^4.5.1, @codetrix-studio/capacitor-google-auth@^3.4.0-rc.4, react@^19.2.0 (+14 more)

### Community 23 - "Data Models & DTO Schemas"
Cohesion: 0.09
Nodes (21): compress, X-Robots-Tag, browserXssFilter, contentTypeNosniff, customFrameOptionsValue, customResponseHeaders, forceSTSHeader, referrerPolicy (+13 more)

### Community 24 - "Data Models & DTO Schemas"
Cohesion: 0.11
Nodes (6): get_mongodb_url(), get_client(), add_security_headers(), lifespan(), start_scheduler(), stop_scheduler()

### Community 25 - "Data Models & DTO Schemas"
Cohesion: 0.13
Nodes (9): _cleanup_old_processed_messages(), _extract_media_paths(), _is_message_already_processed(), _mark_message_as_processed(), MessageProcessingData, _process_message_request(), SessionUpdateData, _update_status_cache() (+1 more)

### Community 26 - "WhatsApp Integration Service"
Cohesion: 0.15
Nodes (4): _delete_latest_status(), test_delete_nonexistent_status(), test_status_deletion_detailed(), test_status_existence_check()

### Community 27 - "Authentication & Tokens"
Cohesion: 0.13
Nodes (12): ProfilePage, IconLogout(), AuthContext, ProfilePage(), api, API_BASE_URL, authAPI, creditsAPI (+4 more)

### Community 28 - "Data Models & DTO Schemas"
Cohesion: 0.21
Nodes (11): get_domains_collection(), build_avatar_image_prompt(), build_domain_image_prompt(), _build_image_request_prompt(), build_style_improvement_prompt(), generate_and_save_image(), _get_image_output_path(), get_or_generate_domain_image() (+3 more)

### Community 29 - "Application Configuration"
Cohesion: 0.14
Nodes (17): devDependencies, eslint@^9.39.1, @eslint/js@^9.39.1, eslint-plugin-react-hooks@^7.0.1, eslint-plugin-react-refresh@^0.4.24, globals@^16.5.0, tailwindcss@^4.1.0, @types/react@^19.2.5 (+9 more)

### Community 30 - "Image Generation & Prompts"
Cohesion: 0.19
Nodes (7): FakeGeminiClient, FakeGeneratedImage, FakeWebImage, test_generate_and_save_image_returns_cached_path_without_calling_client(), test_generate_and_save_image_uses_existing_source_image_for_edit(), test_generate_and_save_image_uses_first_image_when_no_generated_image(), test_generate_and_save_image_uses_generated_image_save()

### Community 31 - "Android & Mobile Pipeline"
Cohesion: 0.15
Nodes (3): get_local_ip(), main(), remove_precompressed_dist_assets()

### Community 33 - "Data Models & DTO Schemas"
Cohesion: 0.19
Nodes (7): get_domain_images_collection(), _compute_domain_stats(), get_domain(), list_domains(), Domain, DomainStats, DomainWithStats

### Community 34 - "Flashcards Generation & SRS"
Cohesion: 0.21
Nodes (5): delete_card(), remove_card_image(), test_generation(), test_generation(), test_generation()

### Community 35 - "Data Models & DTO Schemas"
Cohesion: 0.18
Nodes (5): get_my_profile(), remove_avatar(), update_my_profile(), Profile, ProfileUpdate

### Community 36 - "Data Models & DTO Schemas"
Cohesion: 0.16
Nodes (4): _handle_status_view(), receive_whatsapp_webhook(), get_webhook_dependencies(), WebhookDependencies

### Community 37 - "Setup Cookies Module"
Cohesion: 0.18
Nodes (5): Gemini WebAPI Integration, main(), setup_cookies(), test_cookies(), update_env_file()

### Community 38 - "Navigation & UI Atoms"
Cohesion: 0.30
Nodes (11): defaultProps, IconLog(), IconLogo(), IconProgress(), IconQuestions(), IconStudy(), IconTarget(), IconTime() (+3 more)

### Community 39 - "Application Configuration"
Cohesion: 0.14
Nodes (13): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, resolveJsonModule (+5 more)

### Community 40 - "WhatsApp Integration Service"
Cohesion: 0.18
Nodes (6): AgentCache, Instagram Post Prompt, LinkedIn Post Prompt, WhatsApp Status Prompt, process_message_with_agent(), Google Gemini

### Community 41 - "Flashcards Generation & SRS"
Cohesion: 0.18
Nodes (4): get_reviews_collection(), get_scheduler_status(), _send_srs_daily_reminder(), setup_scheduler()

### Community 42 - "WhatsApp Integration Service"
Cohesion: 0.17
Nodes (5): _check_rate_limit(), _format_viewers_text(), _generate_status_caption(), _manage_recent_viewers(), process_status_viewed_for_image_generation()

### Community 43 - "Docker & Container Infrastructure"
Cohesion: 0.15
Nodes (13): VITE_APPLE_CLIENT_ID, VITE_APPLE_REDIRECT_URI, VITE_GOOGLE_CLIENT_ID, args, context, dockerfile, build, container_name (+5 more)

### Community 44 - "WhatsApp Integration Service"
Cohesion: 0.15
Nodes (12): @capacitor/status-bar@^6.0.3, localforage@^1.10.0, react-chartjs-2@^5.3.1, typescript@^5.9.3, name, private, type, version (+4 more)

### Community 45 - "Navigation & UI Atoms"
Cohesion: 0.15
Nodes (12): background_color, categories, description, display, icons, name, orientation, scope (+4 more)

### Community 46 - "Data Models & DTO Schemas"
Cohesion: 0.24
Nodes (6): get_activity(), get_dashboard(), get_radar(), ActivityEntry, DashboardOverview, RadarEntry

### Community 47 - "Database & MongoDB Connections"
Cohesion: 0.17
Nodes (12): mongodb, build, command, container_name, depends_on, env_file, networks, ports (+4 more)

### Community 48 - "Authentication & Tokens"
Cohesion: 0.17
Nodes (12): MONGO_INITDB_DATABASE, MONGO_INITDB_ROOT_PASSWORD, MONGO_INITDB_ROOT_USERNAME, container_name, env_file, environment, image, networks (+4 more)

### Community 49 - "Application Configuration"
Cohesion: 0.17
Nodes (10): @tailwindcss/vite@^4.1.0, vite@^7.2.4, vite-plugin-compression@^0.5.1, vite-plugin-pwa@^1.2.0, @vitejs/plugin-react@^5.1.1, @tailwindcss/vite, vite, vite-plugin-compression (+2 more)

### Community 50 - "Database & MongoDB Connections"
Cohesion: 0.27
Nodes (6): close_db_connection(), get_profiles_collection(), get_users_collection(), _get_or_create_profile(), create_admin_interactive(), main()

### Community 52 - "Automated Test Suite"
Cohesion: 0.29
Nodes (4): cpu_bound_task(), run_processes(), run_threads(), test_threading_vs_multiprocessing()

### Community 53 - "WhatsApp Integration Service"
Cohesion: 0.18
Nodes (10): networks, whatsapp-network, services, volumes, gemini_cookies, generated_media, har_and_cookies, mongodb_data (+2 more)

### Community 54 - "Docker & Container Infrastructure"
Cohesion: 0.18
Nodes (11): context, dockerfile, build, container_name, depends_on, environment, networks, ports (+3 more)

### Community 55 - "Database & MongoDB Connections"
Cohesion: 0.18
Nodes (11): mongodb, build, command, container_name, depends_on, env_file, networks, restart (+3 more)

### Community 56 - "Authentication & Tokens"
Cohesion: 0.18
Nodes (11): MONGO_INITDB_DATABASE, MONGO_INITDB_ROOT_PASSWORD, MONGO_INITDB_ROOT_USERNAME, container_name, env_file, environment, image, networks (+3 more)

### Community 57 - "Data Models & DTO Schemas"
Cohesion: 0.28
Nodes (3): generate_avatar(), _generate_and_update(), upload_avatar()

### Community 59 - "WhatsApp Integration Service"
Cohesion: 0.22
Nodes (8): networks, whatsapp-network, services, volumes, gemini_cookies, letsencrypt, mongodb_data, driver

### Community 60 - "Docker & Container Infrastructure"
Cohesion: 0.22
Nodes (9): ACME_EMAIL, traefik, container_name, environment, image, networks, ports, restart (+1 more)

### Community 61 - "Docker & Container Infrastructure"
Cohesion: 0.50
Nodes (9): healthcheck, healthcheck, interval, retries, start_period, test, timeout, healthcheck (+1 more)

### Community 62 - "Knowledge Domains Management"
Cohesion: 0.50
Nodes (7): defaultProps, IconDashboard(), IconDomains(), IconProfile(), IconTrain(), IconVisual(), BottomNav()

### Community 63 - "WhatsApp Integration Service"
Cohesion: 0.29
Nodes (3): process_status_view(), extract_primary_user_number(), extract_user_number()

### Community 64 - "Docker & Container Infrastructure"
Cohesion: 0.36
Nodes (8): logging, logging, driver, options, logging, max-file, max-size, logging

### Community 66 - "Android & Mobile Pipeline"
Cohesion: 0.29
Nodes (3): display_and_optionally_install_apk(), get_adb_device(), run()

### Community 69 - "Docker & Container Infrastructure"
Cohesion: 0.29
Nodes (7): watch, develop, develop, action, ignore, path, target

### Community 70 - "Docker & Container Infrastructure"
Cohesion: 0.48
Nodes (7): healthcheck, interval, retries, start_period, test, timeout, healthcheck

### Community 71 - "Docker & Container Infrastructure"
Cohesion: 0.29
Nodes (7): resources, deploy, deploy, memory, deploy, limits, deploy

### Community 72 - "Frontend Tooling & Dependencies"
Cohesion: 0.29
Nodes (4): i18next@^25.8.13, i18next-browser-languagedetector@^8.2.1, i18next, i18next-browser-languagedetector

### Community 74 - "Android & Mobile Pipeline"
Cohesion: 0.47
Nodes (3): convert_svg_to_png(), ensure_cairosvg(), main()

### Community 77 - "Docker & Container Infrastructure"
Cohesion: 0.40
Nodes (5): logging, driver, options, max-file, max-size

### Community 78 - "Frontend Tooling & Dependencies"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

### Community 79 - "Application Configuration"
Cohesion: 0.50
Nodes (3): config, @capacitor/cli@^8.1.0, @capacitor/cli

### Community 82 - "Database & MongoDB Connections"
Cohesion: 0.67
Nodes (3): MongoDB, React 19, OmniFlash (Klique API)

## Knowledge Gaps
- **293 isolated node(s):** `name`, `branches`, `workflow_dispatch`, `contents`, `runs-on` (+288 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 619 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `services` connect `WhatsApp Integration Service` to `Authentication & Tokens`, `Docker & Container Infrastructure`, `Docker & Container Infrastructure`, `Database & MongoDB Connections`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **What connects `name`, `branches`, `workflow_dispatch` to the rest of the system?**
  _293 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Billing & PIX Payments` be split into smaller, more focused modules?**
  _Cohesion score 0.0782312925170068 - nodes in this community are weakly interconnected._
- **Why does `fastapi-app` connect `Database & MongoDB Connections` to `Docker & Container Infrastructure`, `Billing & PIX Payments`, `Docker & Container Infrastructure`, `Docker & Container Infrastructure`?**
  _High betweenness centrality (0.000) - this node is a cross-community bridge._
- **Should `Billing & PIX Payments` be split into smaller, more focused modules?**
  _Cohesion score 0.07092198581560284 - nodes in this community are weakly interconnected._
- **Why does `WhatsAppService` connect `WhatsApp Integration Service` to `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `Avatar & Visual Comparisons`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `WhatsApp Integration Service`, `Avatar & Visual Comparisons`?**
  _High betweenness centrality (0.000) - this node is a cross-community bridge._
- **Should `Apple & Native Auth` be split into smaller, more focused modules?**
  _Cohesion score 0.12525252525252525 - nodes in this community are weakly interconnected._