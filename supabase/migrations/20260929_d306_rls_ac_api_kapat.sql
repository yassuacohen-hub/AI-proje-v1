-- D-306: Veri API kapatma + RLS (KAHIN 2026-09-29)
-- uretim: 2026-09-29T22:50:40
-- service_role DOKUNULMAZ: backend/panel calisir.

-- 1) RLS'i tum tablolarda ac. Parola sizsa bile PostgREST
--    uzerinden satir okunamaz.
ALTER TABLE public."admin_audit_log" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."admin_kvkk_mode" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."admin_mfa" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."admin_mfa_login_tokens" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."admin_mfa_setup_tokens" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."api_usage_daily" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."audit_logs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."campaign_packages" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."campaign_segments" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."campaigns" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."certifications" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."commercial_signals" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."companies" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_aliases" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_capabilities" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_contacts" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_events" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_identifiers" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_industries" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_intelligence_scores" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_locations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_names" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_packages" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_products" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_signals" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_state" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."company_tech_profile" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."credit_ledger" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."entity_matches" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."entity_resolution" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."evidence" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."job_postings" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."key_personnel" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."kvkk_bireysel_email_yedek" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."login_events" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."module_cost" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."momentum_snapshot" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."nace_codes" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."osbs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."packages" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."plan_field_group" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."product_categories" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."products" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."quarantine_firms" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."schema_migrations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."search_events" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."segment_companies" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."segments" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."source_records" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."sources" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."user_activity_log" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."users" ENABLE ROW LEVEL SECURITY;

-- 2) API rollerinden yetkileri geri al -> Veri API kapanir.
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon;
REVOKE ALL ON SCHEMA public FROM anon;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM authenticated;
REVOKE ALL ON SCHEMA public FROM authenticated;

-- 3) Gelecek migration'lara GRANT EKLEMEYIN. 30 Ekim 2026
--    sonrasi Supabase zaten GRANT'siz yeni tablolari API'ye
--    kapatacak; bu bizim istegimizle ayni sonuc verir.
