package com.example.utils;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * SpringBoot工具类项目启动类
 *
 * @author system
 * @date 2025-12-30
 */
@SpringBootApplication
public class UtilsApplication {

    public static void main(String[] args) {
        SpringApplication.run(UtilsApplication.class, args);
        System.out.println("========================================");
        System.out.println("工具类项目启动成功！");
        System.out.println("访问地址: http://localhost:8080");
        System.out.println("========================================");
    }
}
