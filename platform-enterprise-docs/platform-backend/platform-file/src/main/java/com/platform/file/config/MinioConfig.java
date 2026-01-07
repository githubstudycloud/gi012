package com.platform.file.config;

import io.minio.MinioClient;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * MinIO 配置
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "platform.minio")
public class MinioConfig {

    /**
     * MinIO 服务地址
     */
    private String endpoint = "http://localhost:9000";

    /**
     * 访问密钥
     */
    private String accessKey = "minioadmin";

    /**
     * 密钥
     */
    private String secretKey = "minioadmin";

    /**
     * 默认存储桶
     */
    private String defaultBucket = "platform";

    @Bean
    public MinioClient minioClient() {
        return MinioClient.builder()
                .endpoint(endpoint)
                .credentials(accessKey, secretKey)
                .build();
    }
}
