package com.example.utils.controller;

import com.example.utils.CacheManager;
import com.example.utils.IpUtil;
import com.example.utils.SystemInfoUtil;
import com.example.utils.TraceLogUtil;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.Map;

/**
 * 工具类测试Controller
 *
 * @author system
 * @date 2025-12-30
 */
@RestController
@RequestMapping("/api/test")
public class TestController {

    /**
     * 测试IP工具
     */
    @GetMapping("/ip")
    public Map<String, Object> testIp(HttpServletRequest request) {
        TraceLogUtil.startTrace();

        Map<String, Object> result = new HashMap<>();
        result.put("realIp", IpUtil.getRealIp(request));
        result.put("localIp", IpUtil.getLocalIp());
        result.put("actualLocalIp", IpUtil.getActualLocalIp());
        result.put("isLocalIpInternal", IpUtil.isInternalIp(IpUtil.getLocalIp()));

        String testIp = "192.168.1.100";
        result.put("testIp", testIp);
        result.put("isValidIPv4", IpUtil.isValidIPv4(testIp));
        result.put("ipToLong", IpUtil.ipToLong(testIp));
        result.put("isInternalIp", IpUtil.isInternalIp(testIp));

        long duration = TraceLogUtil.endTrace();
        result.put("duration", duration + "ms");
        result.put("traceInfo", TraceLogUtil.getFullTraceInfo());

        return result;
    }

    /**
     * 测试缓存工具
     */
    @GetMapping("/cache")
    public Map<String, Object> testCache(@RequestParam(defaultValue = "testKey") String key,
                                         @RequestParam(defaultValue = "testValue") String value) {
        TraceLogUtil.startTrace();

        Map<String, Object> result = new HashMap<>();

        CacheManager.put(key, value);
        result.put("putKey", key);
        result.put("putValue", value);

        Object cachedValue = CacheManager.get(key);
        result.put("cachedValue", cachedValue);

        result.put("cacheSize", CacheManager.size());
        result.put("containsKey", CacheManager.containsKey(key));
        result.put("hitRate", CacheManager.getHitRate());

        long duration = TraceLogUtil.endTrace();
        result.put("duration", duration + "ms");

        return result;
    }

    /**
     * 测试缓存统计
     */
    @GetMapping("/cache/stats")
    public Map<String, Object> testCacheStats() {
        Map<String, Object> result = new HashMap<>();
        result.put("stats", CacheManager.printStats("default"));
        result.put("cacheNames", CacheManager.getCacheNames());
        result.put("cacheCount", CacheManager.getCacheCount());
        return result;
    }

    /**
     * 测试链路追踪
     */
    @GetMapping("/trace")
    public Map<String, Object> testTrace() {
        String traceId = TraceLogUtil.startTrace();

        Map<String, Object> result = new HashMap<>();
        result.put("traceId", traceId);
        result.put("spanId", TraceLogUtil.getSpanId());

        TraceLogUtil.logInfo("测试业务日志");

        String childSpanId = TraceLogUtil.startChildSpan();
        result.put("childSpanId", childSpanId);
        result.put("parentSpanId", TraceLogUtil.getParentSpanId());

        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        long duration = TraceLogUtil.endTrace();
        result.put("duration", duration + "ms");
        result.put("fullTraceInfo", TraceLogUtil.getFullTraceInfo());

        return result;
    }

    /**
     * 测试系统信息工具
     */
    @GetMapping("/system")
    public Map<String, Object> testSystem() {
        TraceLogUtil.startTrace();

        Map<String, Object> result = SystemInfoUtil.getFullSystemInfo();

        long duration = TraceLogUtil.endTrace();
        result.put("requestDuration", duration + "ms");

        return result;
    }

    /**
     * 测试系统CPU信息
     */
    @GetMapping("/system/cpu")
    public Map<String, Object> testSystemCpu() {
        Map<String, Object> result = new HashMap<>();
        result.put("cpuCoreCount", SystemInfoUtil.getCpuCoreCount());
        result.put("systemCpuLoad", SystemInfoUtil.getSystemCpuLoad() + "%");
        result.put("processCpuLoad", SystemInfoUtil.getProcessCpuLoad() + "%");
        return result;
    }

    /**
     * 测试系统内存信息
     */
    @GetMapping("/system/memory")
    public Map<String, Object> testSystemMemory() {
        Map<String, Object> result = new HashMap<>();
        result.put("totalMemory", SystemInfoUtil.getTotalMemoryMB() + "MB");
        result.put("freeMemory", SystemInfoUtil.getFreeMemoryMB() + "MB");
        result.put("usedMemory", SystemInfoUtil.getUsedMemoryMB() + "MB");
        result.put("memoryUsageRate", SystemInfoUtil.getMemoryUsageRate() + "%");
        return result;
    }

    /**
     * 测试JVM信息
     */
    @GetMapping("/system/jvm")
    public Map<String, Object> testSystemJvm() {
        Map<String, Object> result = new HashMap<>();
        result.put("jvmMaxMemory", SystemInfoUtil.getJvmMaxMemoryMB() + "MB");
        result.put("jvmTotalMemory", SystemInfoUtil.getJvmTotalMemoryMB() + "MB");
        result.put("jvmUsedMemory", SystemInfoUtil.getJvmUsedMemoryMB() + "MB");
        result.put("jvmMemoryUsageRate", SystemInfoUtil.getJvmMemoryUsageRate() + "%");
        result.put("jvmUptime", SystemInfoUtil.formatDuration(SystemInfoUtil.getJvmUptime()));
        result.put("threadCount", SystemInfoUtil.getThreadCount());
        result.put("loadedClassCount", SystemInfoUtil.getLoadedClassCount());
        return result;
    }

    /**
     * 健康检查接口
     */
    @GetMapping("/health")
    public Map<String, Object> health() {
        Map<String, Object> result = new HashMap<>();
        result.put("status", "UP");
        result.put("timestamp", System.currentTimeMillis());
        result.put("message", "工具类项目运行正常");
        return result;
    }

    /**
     * 首页
     */
    @GetMapping("/")
    public Map<String, Object> index() {
        Map<String, Object> result = new HashMap<>();
        result.put("name", "SpringBoot工具类项目");
        result.put("version", "1.0.0");
        result.put("description", "提供IP工具、缓存管理、链路追踪、系统信息等实用工具");
        result.put("availableApis", new String[]{
                "/api/test/ip - IP工具测试",
                "/api/test/cache - 缓存工具测试",
                "/api/test/cache/stats - 缓存统计",
                "/api/test/trace - 链路追踪测试",
                "/api/test/system - 系统完整信息",
                "/api/test/system/cpu - CPU信息",
                "/api/test/system/memory - 内存信息",
                "/api/test/system/jvm - JVM信息",
                "/api/test/health - 健康检查"
        });
        return result;
    }
}
