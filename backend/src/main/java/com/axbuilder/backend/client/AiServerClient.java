package com.axbuilder.backend.client;

import com.axbuilder.backend.config.AxBuilderProperties;
import com.axbuilder.backend.dto.AiServerExecutionRequest;
import com.axbuilder.backend.dto.AiServerExecutionResponse;
import org.springframework.http.MediaType;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.net.http.HttpClient;
import java.time.Duration;

@Component
public class AiServerClient {

    private final RestClient restClient;

    public AiServerClient(RestClient.Builder builder, AxBuilderProperties properties) {
        HttpClient httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(properties.timeoutSeconds()))
                .build();

        JdkClientHttpRequestFactory requestFactory = new JdkClientHttpRequestFactory(httpClient);
        requestFactory.setReadTimeout(Duration.ofSeconds(properties.timeoutSeconds()));

        this.restClient = builder
                .baseUrl(properties.baseUrl())
                .requestFactory(requestFactory)
                .build();
    }

    public AiServerExecutionResponse execute(AiServerExecutionRequest request) {
        AiServerExecutionResponse response = restClient.post()
                .uri("/v1/agents/execute")
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(AiServerExecutionResponse.class);

        if (response == null) {
            throw new IllegalStateException("AI Server 응답이 비어 있습니다.");
        }
        return response;
    }
}
