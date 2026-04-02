import { useI18n } from "../i18n";

/**
 * Handle language selector for the current workflow.
 */
export function LanguageSelector() {
  const { language, setLanguage, t } = useI18n();

  return (
    <label className="search-chip" htmlFor="language-selector">
      <span>{t("common.language")}</span>
      <select
        id="language-selector"
        value={language}
        onChange={(event) => setLanguage(event.target.value as "ko" | "en")}
      >
        <option value="ko">{t("common.korean")}</option>
        <option value="en">{t("common.english")}</option>
      </select>
    </label>
  );
}
