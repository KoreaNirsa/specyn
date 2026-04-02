"""
`backend build` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "dashboard" / "backend"


def test_backend_build_imports_spring_boot_bom_for_versionless_dependencies() -> None:
    """
    회귀 테스트로서 `backend_build_imports_spring_boot_bom_for_versionless_dependencies` 시나리오를 검증한다.

    주요 흐름은 `read_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.
    """
    content = (ROOT / "build.gradle.kts").read_text(encoding="utf-8")

    expected_platform_declarations = [
        "implementation(platform(org.springframework.boot.gradle.plugin.SpringBootPlugin.BOM_COORDINATES))",
        "compileOnly(platform(org.springframework.boot.gradle.plugin.SpringBootPlugin.BOM_COORDINATES))",
        "annotationProcessor(platform(org.springframework.boot.gradle.plugin.SpringBootPlugin.BOM_COORDINATES))",
        "testImplementation(platform(org.springframework.boot.gradle.plugin.SpringBootPlugin.BOM_COORDINATES))",
        "testCompileOnly(platform(org.springframework.boot.gradle.plugin.SpringBootPlugin.BOM_COORDINATES))",
        "testAnnotationProcessor(platform(org.springframework.boot.gradle.plugin.SpringBootPlugin.BOM_COORDINATES))",
    ]

    for declaration in expected_platform_declarations:
        assert declaration in content


def test_backend_build_declares_spring_boot_restclient_dependency() -> None:
    """
    회귀 테스트로서 `backend_build_declares_spring_boot_restclient_dependency` 시나리오를 검증한다.

    주요 흐름은 `read_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    content = (ROOT / "build.gradle.kts").read_text(encoding="utf-8")

    assert 'implementation("org.springframework.boot:spring-boot-restclient")' in content


def test_ai_server_client_uses_http_client_builder_for_connect_timeout() -> None:
    """
    회귀 테스트로서 `ai_server_client_uses_http_client_builder_for_connect_timeout` 시나리오를 검증한다.

    주요 흐름은 `read_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    content = (ROOT / "src" / "main" / "java" / "com" / "axbuilder" / "backend" / "client" / "AiServerClient.java").read_text(
        encoding="utf-8"
    )

    assert "HttpClient.newBuilder()" in content
    assert ".connectTimeout(Duration.ofSeconds(properties.timeoutSeconds()))" in content
    assert "new JdkClientHttpRequestFactory(httpClient)" in content
    assert "requestFactory.setReadTimeout(Duration.ofSeconds(properties.timeoutSeconds()))" in content
    assert "setConnectTimeout(" not in content


def test_security_config_disables_generated_dev_user_when_security_is_off() -> None:
    """
    회귀 테스트로서 `security_config_disables_generated_dev_user_when_security_is_off` 시나리오를 검증한다.

    주요 흐름은 `read_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    content = (ROOT / "src" / "main" / "java" / "com" / "axbuilder" / "backend" / "config" / "SecurityConfig.java").read_text(
        encoding="utf-8"
    )

    assert '@ConditionalOnProperty(name = "axbuilder.security.enabled", havingValue = "false", matchIfMissing = true)' in content
    assert "public UserDetailsService noLocalLoginUserDetailsService()" in content
