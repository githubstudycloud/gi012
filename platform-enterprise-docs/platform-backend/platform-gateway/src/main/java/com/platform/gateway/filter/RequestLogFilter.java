package com.platform.gateway.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.UUID;

/**
 * 请求日志过滤器
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Slf4j
@Component
public class RequestLogFilter implements GlobalFilter, Ordered {

    private static final String REQUEST_TIME_ATTR = "requestTime";
    private static final String REQUEST_ID_ATTR = "requestId";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String requestId = UUID.randomUUID().toString().replace("-", "");
        long startTime = System.currentTimeMillis();

        ServerHttpRequest request = exchange.getRequest();

        // 记录请求信息
        log.info("[{}] >>> {} {} - {}",
                requestId,
                request.getMethod(),
                request.getURI().getPath(),
                request.getRemoteAddress()
        );

        // 添加请求ID到请求头
        ServerHttpRequest mutatedRequest = request.mutate()
                .header("X-Request-Id", requestId)
                .build();

        return chain.filter(exchange.mutate().request(mutatedRequest).build())
                .doOnSuccess(aVoid -> {
                    long duration = System.currentTimeMillis() - startTime;
                    log.info("[{}] <<< {} {} - {}ms",
                            requestId,
                            request.getMethod(),
                            request.getURI().getPath(),
                            duration
                    );
                })
                .doOnError(throwable -> {
                    long duration = System.currentTimeMillis() - startTime;
                    log.error("[{}] !!! {} {} - {}ms - Error: {}",
                            requestId,
                            request.getMethod(),
                            request.getURI().getPath(),
                            duration,
                            throwable.getMessage()
                    );
                });
    }

    @Override
    public int getOrder() {
        return -200;
    }
}
