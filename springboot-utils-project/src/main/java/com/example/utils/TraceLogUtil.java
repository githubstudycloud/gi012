package com.example.utils;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

import java.util.UUID;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 请求链路追踪工具类
 * 用于生成和管理TraceID,实现分布式请求链路追踪
 *
 * @author system
 * @date 2025-12-30
 */
public class TraceLogUtil {

    private static final Logger logger = LoggerFactory.getLogger(TraceLogUtil.class);

    private static final String TRACE_ID = "traceId";
    private static final String SPAN_ID = "spanId";
    private static final String PARENT_SPAN_ID = "parentSpanId";
    private static final String START_TIME = "startTime";

    private static final ThreadLocal<String> TRACE_ID_HOLDER = new ThreadLocal<>();
    private static final ThreadLocal<String> SPAN_ID_HOLDER = new ThreadLocal<>();
    private static final ThreadLocal<String> PARENT_SPAN_ID_HOLDER = new ThreadLocal<>();
    private static final ThreadLocal<Long> START_TIME_HOLDER = new ThreadLocal<>();

    private static final AtomicLong SPAN_COUNTER = new AtomicLong(0);
    private static final String TRACE_PREFIX = "TRC";
    private static final String SPAN_PREFIX = "SPN";

    /**
     * 生成TraceID
     */
    public static String generateTraceId() {
        String uuid = UUID.randomUUID().toString().replace("-", "");
        long timestamp = System.currentTimeMillis();
        return TRACE_PREFIX + "-" + timestamp + "-" + uuid.substring(0, 16);
    }

    /**
     * 生成SpanID
     */
    public static String generateSpanId() {
        long counter = SPAN_COUNTER.incrementAndGet();
        long timestamp = System.currentTimeMillis();
        return SPAN_PREFIX + "-" + timestamp + "-" + counter;
    }

    /**
     * 开始追踪(新建TraceID)
     */
    public static String startTrace() {
        String traceId = generateTraceId();
        String spanId = generateSpanId();
        long startTime = System.currentTimeMillis();

        setTraceId(traceId);
        setSpanId(spanId);
        setStartTime(startTime);

        putToMdc(TRACE_ID, traceId);
        putToMdc(SPAN_ID, spanId);
        putToMdc(START_TIME, String.valueOf(startTime));

        return traceId;
    }

    /**
     * 开始追踪(使用已有TraceID)
     */
    public static String startTrace(String traceId) {
        if (traceId == null || traceId.isEmpty()) {
            return startTrace();
        }

        String spanId = generateSpanId();
        long startTime = System.currentTimeMillis();

        setTraceId(traceId);
        setSpanId(spanId);
        setStartTime(startTime);

        putToMdc(TRACE_ID, traceId);
        putToMdc(SPAN_ID, spanId);
        putToMdc(START_TIME, String.valueOf(startTime));

        return traceId;
    }

    /**
     * 开始子Span追踪
     */
    public static String startChildSpan() {
        String currentSpanId = getSpanId();
        String childSpanId = generateSpanId();

        setParentSpanId(currentSpanId);
        setSpanId(childSpanId);

        putToMdc(PARENT_SPAN_ID, currentSpanId);
        putToMdc(SPAN_ID, childSpanId);

        return childSpanId;
    }

    /**
     * 结束追踪并返回耗时
     */
    public static long endTrace() {
        long endTime = System.currentTimeMillis();
        Long startTime = getStartTime();

        long duration = 0L;
        if (startTime != null) {
            duration = endTime - startTime;
        }

        logTraceInfo(duration);
        clearTrace();

        return duration;
    }

    /**
     * 记录追踪信息
     */
    private static void logTraceInfo(long duration) {
        String traceId = getTraceId();
        String spanId = getSpanId();

        if (traceId != null && spanId != null) {
            logger.debug("TraceID: {}, SpanID: {}, Duration: {}ms",
                    traceId, spanId, duration);
        }
    }

    /**
     * 清理追踪信息
     */
    public static void clearTrace() {
        TRACE_ID_HOLDER.remove();
        SPAN_ID_HOLDER.remove();
        PARENT_SPAN_ID_HOLDER.remove();
        START_TIME_HOLDER.remove();

        MDC.remove(TRACE_ID);
        MDC.remove(SPAN_ID);
        MDC.remove(PARENT_SPAN_ID);
        MDC.remove(START_TIME);
    }

    /**
     * 设置TraceID
     */
    public static void setTraceId(String traceId) {
        if (traceId != null && !traceId.isEmpty()) {
            TRACE_ID_HOLDER.set(traceId);
        }
    }

    /**
     * 获取TraceID
     */
    public static String getTraceId() {
        return TRACE_ID_HOLDER.get();
    }

    /**
     * 设置SpanID
     */
    public static void setSpanId(String spanId) {
        if (spanId != null && !spanId.isEmpty()) {
            SPAN_ID_HOLDER.set(spanId);
        }
    }

    /**
     * 获取SpanID
     */
    public static String getSpanId() {
        return SPAN_ID_HOLDER.get();
    }

    /**
     * 设置ParentSpanID
     */
    public static void setParentSpanId(String parentSpanId) {
        if (parentSpanId != null && !parentSpanId.isEmpty()) {
            PARENT_SPAN_ID_HOLDER.set(parentSpanId);
        }
    }

    /**
     * 获取ParentSpanID
     */
    public static String getParentSpanId() {
        return PARENT_SPAN_ID_HOLDER.get();
    }

    /**
     * 设置开始时间
     */
    public static void setStartTime(long startTime) {
        START_TIME_HOLDER.set(startTime);
    }

    /**
     * 获取开始时间
     */
    public static Long getStartTime() {
        return START_TIME_HOLDER.get();
    }

    /**
     * 获取当前耗时(毫秒)
     */
    public static long getCurrentDuration() {
        Long startTime = getStartTime();
        if (startTime == null) {
            return 0L;
        }
        return System.currentTimeMillis() - startTime;
    }

    /**
     * 添加到MDC
     */
    private static void putToMdc(String key, String value) {
        if (key != null && value != null) {
            MDC.put(key, value);
        }
    }

    /**
     * 判断是否存在TraceID
     */
    public static boolean hasTraceId() {
        return getTraceId() != null;
    }

    /**
     * 获取完整追踪信息
     */
    public static String getFullTraceInfo() {
        String traceId = getTraceId();
        String spanId = getSpanId();
        String parentSpanId = getParentSpanId();
        long duration = getCurrentDuration();

        return buildTraceInfo(traceId, spanId, parentSpanId, duration);
    }

    /**
     * 构建追踪信息字符串
     */
    private static String buildTraceInfo(String traceId, String spanId,
                                         String parentSpanId, long duration) {
        StringBuilder sb = new StringBuilder();
        sb.append("TraceID: ").append(traceId != null ? traceId : "N/A");
        sb.append(", SpanID: ").append(spanId != null ? spanId : "N/A");

        if (parentSpanId != null) {
            sb.append(", ParentSpanID: ").append(parentSpanId);
        }

        sb.append(", Duration: ").append(duration).append("ms");
        return sb.toString();
    }

    /**
     * 记录业务日志(自动附加TraceID)
     */
    public static void logInfo(String message) {
        String traceId = getTraceId();
        if (traceId != null) {
            logger.info("[{}] {}", traceId, message);
        } else {
            logger.info(message);
        }
    }

    /**
     * 记录错误日志(自动附加TraceID)
     */
    public static void logError(String message, Throwable throwable) {
        String traceId = getTraceId();
        if (traceId != null) {
            logger.error("[{}] {}", traceId, message, throwable);
        } else {
            logger.error(message, throwable);
        }
    }

    /**
     * 记录警告日志(自动附加TraceID)
     */
    public static void logWarn(String message) {
        String traceId = getTraceId();
        if (traceId != null) {
            logger.warn("[{}] {}", traceId, message);
        } else {
            logger.warn(message);
        }
    }

    /**
     * 创建TraceContext快照
     */
    public static TraceContext snapshot() {
        return new TraceContext(
                getTraceId(),
                getSpanId(),
                getParentSpanId(),
                getStartTime()
        );
    }

    /**
     * 恢复TraceContext
     */
    public static void restore(TraceContext context) {
        if (context == null) {
            return;
        }

        if (context.getTraceId() != null) {
            setTraceId(context.getTraceId());
            putToMdc(TRACE_ID, context.getTraceId());
        }

        if (context.getSpanId() != null) {
            setSpanId(context.getSpanId());
            putToMdc(SPAN_ID, context.getSpanId());
        }

        if (context.getParentSpanId() != null) {
            setParentSpanId(context.getParentSpanId());
            putToMdc(PARENT_SPAN_ID, context.getParentSpanId());
        }

        if (context.getStartTime() != null) {
            setStartTime(context.getStartTime());
            putToMdc(START_TIME, String.valueOf(context.getStartTime()));
        }
    }

    /**
     * TraceContext上下文类
     */
    public static class TraceContext {
        private final String traceId;
        private final String spanId;
        private final String parentSpanId;
        private final Long startTime;

        public TraceContext(String traceId, String spanId,
                           String parentSpanId, Long startTime) {
            this.traceId = traceId;
            this.spanId = spanId;
            this.parentSpanId = parentSpanId;
            this.startTime = startTime;
        }

        public String getTraceId() {
            return traceId;
        }

        public String getSpanId() {
            return spanId;
        }

        public String getParentSpanId() {
            return parentSpanId;
        }

        public Long getStartTime() {
            return startTime;
        }
    }
}
