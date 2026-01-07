package com.platform.file;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

/**
 * 文件服务启动类
 *
 * @author Platform Team
 * @since 1.0.0
 */
@SpringBootApplication
@ComponentScan(basePackages = {"com.platform"})
public class FileApplication {

    public static void main(String[] args) {
        SpringApplication.run(FileApplication.class, args);
    }
}
