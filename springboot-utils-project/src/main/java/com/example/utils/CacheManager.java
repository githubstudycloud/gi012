package com.example.utils;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import com.github.benmanes.caffeine.cache.stats.CacheStats;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import java.util.function.Function;

/**
 * 本地缓存管理器
 * 基于Caffeine实现的高性能本地缓存
 *
 * @author system
 * @date 2025-12-30
 */
public class CacheManager {

    private static final Map<String, Cache<String, Object>> CACHE_MAP = new ConcurrentHashMap<>();

    private static final long DEFAULT_EXPIRE_SECONDS = 3600L;
    private static final long DEFAULT_MAX_SIZE = 10000L;
    private static final String DEFAULT_CACHE_NAME = "default";

    /**
     * 获取默认缓存实例
     */
    public static Cache<String, Object> getDefaultCache() {
        return getCache(DEFAULT_CACHE_NAME);
    }

    /**
     * 获取指定名称的缓存实例
     */
    public static Cache<String, Object> getCache(String cacheName) {
        if (cacheName == null || cacheName.isEmpty()) {
            cacheName = DEFAULT_CACHE_NAME;
        }

        return CACHE_MAP.computeIfAbsent(cacheName, key -> {
            return buildCache(DEFAULT_EXPIRE_SECONDS, DEFAULT_MAX_SIZE);
        });
    }

    /**
     * 创建自定义配置的缓存
     */
    public static Cache<String, Object> createCache(String cacheName,
                                                     long expireSeconds,
                                                     long maxSize) {
        if (cacheName == null || cacheName.isEmpty()) {
            return null;
        }

        Cache<String, Object> cache = buildCache(expireSeconds, maxSize);
        CACHE_MAP.put(cacheName, cache);
        return cache;
    }

    /**
     * 构建缓存实例
     */
    private static Cache<String, Object> buildCache(long expireSeconds, long maxSize) {
        return Caffeine.newBuilder()
                .expireAfterWrite(expireSeconds, TimeUnit.SECONDS)
                .maximumSize(maxSize)
                .recordStats()
                .build();
    }

    /**
     * 设置缓存值(使用默认缓存)
     */
    public static void put(String key, Object value) {
        if (key == null || value == null) {
            return;
        }
        getDefaultCache().put(key, value);
    }

    /**
     * 设置缓存值(指定缓存名称)
     */
    public static void put(String cacheName, String key, Object value) {
        if (key == null || value == null) {
            return;
        }
        getCache(cacheName).put(key, value);
    }

    /**
     * 获取缓存值(使用默认缓存)
     */
    public static Object get(String key) {
        if (key == null) {
            return null;
        }
        return getDefaultCache().getIfPresent(key);
    }

    /**
     * 获取缓存值(指定缓存名称)
     */
    public static Object get(String cacheName, String key) {
        if (key == null) {
            return null;
        }
        return getCache(cacheName).getIfPresent(key);
    }

    /**
     * 获取缓存值,如果不存在则加载
     */
    public static Object getOrLoad(String key, Function<String, Object> loader) {
        if (key == null || loader == null) {
            return null;
        }
        return getDefaultCache().get(key, loader);
    }

    /**
     * 获取缓存值,如果不存在则加载(指定缓存名称)
     */
    public static Object getOrLoad(String cacheName, String key,
                                   Function<String, Object> loader) {
        if (key == null || loader == null) {
            return null;
        }
        return getCache(cacheName).get(key, loader);
    }

    /**
     * 删除缓存(使用默认缓存)
     */
    public static void remove(String key) {
        if (key == null) {
            return;
        }
        getDefaultCache().invalidate(key);
    }

    /**
     * 删除缓存(指定缓存名称)
     */
    public static void remove(String cacheName, String key) {
        if (key == null) {
            return;
        }
        getCache(cacheName).invalidate(key);
    }

    /**
     * 批量删除缓存(使用默认缓存)
     */
    public static void removeAll(Iterable<String> keys) {
        if (keys == null) {
            return;
        }
        getDefaultCache().invalidateAll(keys);
    }

    /**
     * 批量删除缓存(指定缓存名称)
     */
    public static void removeAll(String cacheName, Iterable<String> keys) {
        if (keys == null) {
            return;
        }
        getCache(cacheName).invalidateAll(keys);
    }

    /**
     * 清空缓存(使用默认缓存)
     */
    public static void clear() {
        getDefaultCache().invalidateAll();
    }

    /**
     * 清空缓存(指定缓存名称)
     */
    public static void clear(String cacheName) {
        getCache(cacheName).invalidateAll();
    }

    /**
     * 清空所有缓存
     */
    public static void clearAll() {
        CACHE_MAP.values().forEach(Cache::invalidateAll);
    }

    /**
     * 获取缓存大小(使用默认缓存)
     */
    public static long size() {
        return getDefaultCache().estimatedSize();
    }

    /**
     * 获取缓存大小(指定缓存名称)
     */
    public static long size(String cacheName) {
        return getCache(cacheName).estimatedSize();
    }

    /**
     * 判断缓存是否存在(使用默认缓存)
     */
    public static boolean containsKey(String key) {
        if (key == null) {
            return false;
        }
        return getDefaultCache().getIfPresent(key) != null;
    }

    /**
     * 判断缓存是否存在(指定缓存名称)
     */
    public static boolean containsKey(String cacheName, String key) {
        if (key == null) {
            return false;
        }
        return getCache(cacheName).getIfPresent(key) != null;
    }

    /**
     * 获取所有缓存键(使用默认缓存)
     */
    public static Map<String, Object> asMap() {
        return getDefaultCache().asMap();
    }

    /**
     * 获取所有缓存键(指定缓存名称)
     */
    public static Map<String, Object> asMap(String cacheName) {
        return getCache(cacheName).asMap();
    }

    /**
     * 获取缓存统计信息(使用默认缓存)
     */
    public static CacheStats getStats() {
        return getDefaultCache().stats();
    }

    /**
     * 获取缓存统计信息(指定缓存名称)
     */
    public static CacheStats getStats(String cacheName) {
        return getCache(cacheName).stats();
    }

    /**
     * 获取缓存命中率(使用默认缓存)
     */
    public static double getHitRate() {
        return getDefaultCache().stats().hitRate();
    }

    /**
     * 获取缓存命中率(指定缓存名称)
     */
    public static double getHitRate(String cacheName) {
        return getCache(cacheName).stats().hitRate();
    }

    /**
     * 手动触发缓存清理
     */
    public static void cleanUp() {
        getDefaultCache().cleanUp();
    }

    /**
     * 手动触发缓存清理(指定缓存名称)
     */
    public static void cleanUp(String cacheName) {
        getCache(cacheName).cleanUp();
    }

    /**
     * 删除指定的缓存实例
     */
    public static void removeCache(String cacheName) {
        if (cacheName == null || cacheName.isEmpty()) {
            return;
        }

        Cache<String, Object> cache = CACHE_MAP.remove(cacheName);
        if (cache != null) {
            cache.invalidateAll();
        }
    }

    /**
     * 获取所有缓存名称
     */
    public static String[] getCacheNames() {
        return CACHE_MAP.keySet().toArray(new String[0]);
    }

    /**
     * 获取缓存数量
     */
    public static int getCacheCount() {
        return CACHE_MAP.size();
    }

    /**
     * 打印缓存统计信息
     */
    public static String printStats(String cacheName) {
        CacheStats stats = getStats(cacheName);
        if (stats == null) {
            return "缓存不存在: " + cacheName;
        }

        return buildStatsString(cacheName, stats);
    }

    /**
     * 构建统计信息字符串
     */
    private static String buildStatsString(String cacheName, CacheStats stats) {
        StringBuilder sb = new StringBuilder();
        sb.append("缓存名称: ").append(cacheName).append("\n");
        sb.append("命中次数: ").append(stats.hitCount()).append("\n");
        sb.append("未命中次数: ").append(stats.missCount()).append("\n");
        sb.append("命中率: ").append(String.format("%.2f%%", stats.hitRate() * 100)).append("\n");
        sb.append("加载成功次数: ").append(stats.loadSuccessCount()).append("\n");
        sb.append("加载失败次数: ").append(stats.loadFailureCount()).append("\n");
        sb.append("淘汰次数: ").append(stats.evictionCount()).append("\n");
        return sb.toString();
    }
}
