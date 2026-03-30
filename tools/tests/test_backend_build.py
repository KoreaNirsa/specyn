from pathlib import Path


def test_backend_build_imports_spring_boot_bom_for_versionless_dependencies() -> None:
    content = Path("backend/build.gradle.kts").read_text(encoding="utf-8")

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
    content = Path("backend/build.gradle.kts").read_text(encoding="utf-8")

    assert 'implementation("org.springframework.boot:spring-boot-restclient")' in content


def test_ai_server_client_uses_http_client_builder_for_connect_timeout() -> None:
    content = Path(
        "backend/src/main/java/com/axbuilder/backend/client/AiServerClient.java"
    ).read_text(encoding="utf-8")

    assert "HttpClient.newBuilder()" in content
    assert ".connectTimeout(Duration.ofSeconds(properties.timeoutSeconds()))" in content
    assert "new JdkClientHttpRequestFactory(httpClient)" in content
    assert "requestFactory.setReadTimeout(Duration.ofSeconds(properties.timeoutSeconds()))" in content
    assert "setConnectTimeout(" not in content


def test_security_config_disables_generated_dev_user_when_security_is_off() -> None:
    content = Path("backend/src/main/java/com/axbuilder/backend/config/SecurityConfig.java").read_text(
        encoding="utf-8"
    )

    assert "@ConditionalOnProperty(name = \"axbuilder.security.enabled\", havingValue = \"false\", matchIfMissing = true)" in content
    assert "public UserDetailsService noLocalLoginUserDetailsService()" in content
