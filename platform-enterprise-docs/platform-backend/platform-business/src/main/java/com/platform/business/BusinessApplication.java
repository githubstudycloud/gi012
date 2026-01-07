package com.platform.business;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

/**
 * 业务服务启动类
 *
 * @author Platform Team
 * @since 1.0.0
 */
@SpringBootApplication
@ComponentScan(basePackages = {"com.platform"})
@MapperScan("com.platform.business.mapper")
public class BusinessApplication {

    public static void main(String[] args) {
        SpringApplication.run(BusinessApplication.class, args);
    }
}
