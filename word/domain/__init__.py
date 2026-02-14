"""word.domain パッケージ — ドメインチェック機能群"""

# domain_check.py からの再エクスポート
from .domain_check import (
    ScreenItem,
    DomainDef,
    TableItem,
    MatchResult,
    load_screen_items,
    load_domains,
    load_table_definitions,
    dedup_by_name_and_digits,
    process_screen_domain_matching,
    process_table_domain_matching,
    save_domain_check_results,
)

# domain_matcher.py からの再エクスポート（ashigaru3 移動待ち）
try:
    from .domain_matcher import (
        MatchEvidence,
        collect_evidence,
        collect_evidence_batch,
        resolve_without_llm,
        build_llm_context,
    )
except ImportError:
    pass

# synonyms.py からの再エクスポート（ashigaru4 移動待ち）
try:
    from .synonyms import (
        are_synonyms,
        get_synonym_group,
        find_synonym_match,
        strip_digits,
    )
except ImportError:
    pass

# llm_matcher.py からの再エクスポート（ashigaru4 移動待ち）
try:
    from .llm_matcher import run_llm_matching
except ImportError:
    pass
