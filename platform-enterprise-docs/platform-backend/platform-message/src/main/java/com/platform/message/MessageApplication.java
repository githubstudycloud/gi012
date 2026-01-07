package com.platform.message;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

/**
 * 消息服务启动类
 *
 * @author Platform Team
 * @since 1.0.0
 */
@SpringBootApplication
@ComponentScan(basePackages = {"com.platform"})
public class MessageApplication {

    public static void main(String[] args) {
        SpringApplication.run(MessageApplication.class, args);
    }
}
