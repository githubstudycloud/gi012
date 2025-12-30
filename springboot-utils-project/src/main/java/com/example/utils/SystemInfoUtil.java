package com.example.utils;

import java.io.File;
import java.lang.management.*;
import java.text.DecimalFormat;
import java.util.HashMap;
import java.util.Map;

/**
 * 系统信息工具类
 * 获取系统CPU、内存、磁盘、JVM等信息
 *
 * @author system
 * @date 2025-12-30
 */
public class SystemInfoUtil {

    private static final long MB = 1024 * 1024;
    private static final long GB = 1024 * 1024 * 1024;
    private static final DecimalFormat DF = new DecimalFormat("0.00");

    /**
     * 获取CPU核心数
     */
    public static int getCpuCoreCount() {
        return Runtime.getRuntime().availableProcessors();
    }

    /**
     * 获取系统CPU负载
     */
    public static double getSystemCpuLoad() {
        OperatingSystemMXBean osBean = ManagementFactory.getOperatingSystemMXBean();
        if (osBean instanceof com.sun.management.OperatingSystemMXBean) {
            com.sun.management.OperatingSystemMXBean sunOsBean =
                    (com.sun.management.OperatingSystemMXBean) osBean;
            double load = sunOsBean.getSystemCpuLoad();
            return load >= 0 ? load * 100 : 0;
        }
        return 0;
    }

    /**
     * 获取进程CPU负载
     */
    public static double getProcessCpuLoad() {
        OperatingSystemMXBean osBean = ManagementFactory.getOperatingSystemMXBean();
        if (osBean instanceof com.sun.management.OperatingSystemMXBean) {
            com.sun.management.OperatingSystemMXBean sunOsBean =
                    (com.sun.management.OperatingSystemMXBean) osBean;
            double load = sunOsBean.getProcessCpuLoad();
            return load >= 0 ? load * 100 : 0;
        }
        return 0;
    }

    /**
     * 获取系统总内存(MB)
     */
    public static long getTotalMemoryMB() {
        OperatingSystemMXBean osBean = ManagementFactory.getOperatingSystemMXBean();
        if (osBean instanceof com.sun.management.OperatingSystemMXBean) {
            com.sun.management.OperatingSystemMXBean sunOsBean =
                    (com.sun.management.OperatingSystemMXBean) osBean;
            return sunOsBean.getTotalPhysicalMemorySize() / MB;
        }
        return 0;
    }

    /**
     * 获取系统空闲内存(MB)
     */
    public static long getFreeMemoryMB() {
        OperatingSystemMXBean osBean = ManagementFactory.getOperatingSystemMXBean();
        if (osBean instanceof com.sun.management.OperatingSystemMXBean) {
            com.sun.management.OperatingSystemMXBean sunOsBean =
                    (com.sun.management.OperatingSystemMXBean) osBean;
            return sunOsBean.getFreePhysicalMemorySize() / MB;
        }
        return 0;
    }

    /**
     * 获取系统已用内存(MB)
     */
    public static long getUsedMemoryMB() {
        return getTotalMemoryMB() - getFreeMemoryMB();
    }

    /**
     * 获取系统内存使用率(%)
     */
    public static double getMemoryUsageRate() {
        long total = getTotalMemoryMB();
        if (total == 0) {
            return 0;
        }
        long used = getUsedMemoryMB();
        return (double) used / total * 100;
    }

    /**
     * 获取JVM最大内存(MB)
     */
    public static long getJvmMaxMemoryMB() {
        return Runtime.getRuntime().maxMemory() / MB;
    }

    /**
     * 获取JVM总内存(MB)
     */
    public static long getJvmTotalMemoryMB() {
        return Runtime.getRuntime().totalMemory() / MB;
    }

    /**
     * 获取JVM空闲内存(MB)
     */
    public static long getJvmFreeMemoryMB() {
        return Runtime.getRuntime().freeMemory() / MB;
    }

    /**
     * 获取JVM已用内存(MB)
     */
    public static long getJvmUsedMemoryMB() {
        return getJvmTotalMemoryMB() - getJvmFreeMemoryMB();
    }

    /**
     * 获取JVM内存使用率(%)
     */
    public static double getJvmMemoryUsageRate() {
        long total = getJvmTotalMemoryMB();
        if (total == 0) {
            return 0;
        }
        long used = getJvmUsedMemoryMB();
        return (double) used / total * 100;
    }

    /**
     * 获取磁盘总空间(GB)
     */
    public static long getDiskTotalSpaceGB() {
        File[] roots = File.listRoots();
        long totalSpace = 0;
        for (File root : roots) {
            totalSpace += root.getTotalSpace();
        }
        return totalSpace / GB;
    }

    /**
     * 获取磁盘可用空间(GB)
     */
    public static long getDiskFreeSpaceGB() {
        File[] roots = File.listRoots();
        long freeSpace = 0;
        for (File root : roots) {
            freeSpace += root.getFreeSpace();
        }
        return freeSpace / GB;
    }

    /**
     * 获取磁盘已用空间(GB)
     */
    public static long getDiskUsedSpaceGB() {
        return getDiskTotalSpaceGB() - getDiskFreeSpaceGB();
    }

    /**
     * 获取磁盘使用率(%)
     */
    public static double getDiskUsageRate() {
        long total = getDiskTotalSpaceGB();
        if (total == 0) {
            return 0;
        }
        long used = getDiskUsedSpaceGB();
        return (double) used / total * 100;
    }

    /**
     * 获取操作系统名称
     */
    public static String getOsName() {
        return System.getProperty("os.name");
    }

    /**
     * 获取操作系统版本
     */
    public static String getOsVersion() {
        return System.getProperty("os.version");
    }

    /**
     * 获取操作系统架构
     */
    public static String getOsArch() {
        return System.getProperty("os.arch");
    }

    /**
     * 获取Java版本
     */
    public static String getJavaVersion() {
        return System.getProperty("java.version");
    }

    /**
     * 获取Java Home路径
     */
    public static String getJavaHome() {
        return System.getProperty("java.home");
    }

    /**
     * 获取JVM名称
     */
    public static String getJvmName() {
        return System.getProperty("java.vm.name");
    }

    /**
     * 获取JVM版本
     */
    public static String getJvmVersion() {
        return System.getProperty("java.vm.version");
    }

    /**
     * 获取JVM启动时间
     */
    public static long getJvmStartTime() {
        RuntimeMXBean runtimeMXBean = ManagementFactory.getRuntimeMXBean();
        return runtimeMXBean.getStartTime();
    }

    /**
     * 获取JVM运行时长(毫秒)
     */
    public static long getJvmUptime() {
        RuntimeMXBean runtimeMXBean = ManagementFactory.getRuntimeMXBean();
        return runtimeMXBean.getUptime();
    }

    /**
     * 获取线程总数
     */
    public static int getThreadCount() {
        ThreadMXBean threadMXBean = ManagementFactory.getThreadMXBean();
        return threadMXBean.getThreadCount();
    }

    /**
     * 获取守护线程数
     */
    public static int getDaemonThreadCount() {
        ThreadMXBean threadMXBean = ManagementFactory.getThreadMXBean();
        return threadMXBean.getDaemonThreadCount();
    }

    /**
     * 获取峰值线程数
     */
    public static int getPeakThreadCount() {
        ThreadMXBean threadMXBean = ManagementFactory.getThreadMXBean();
        return threadMXBean.getPeakThreadCount();
    }

    /**
     * 获取已加载类数量
     */
    public static int getLoadedClassCount() {
        ClassLoadingMXBean classLoadingMXBean = ManagementFactory.getClassLoadingMXBean();
        return classLoadingMXBean.getLoadedClassCount();
    }

    /**
     * 获取已卸载类数量
     */
    public static long getUnloadedClassCount() {
        ClassLoadingMXBean classLoadingMXBean = ManagementFactory.getClassLoadingMXBean();
        return classLoadingMXBean.getUnloadedClassCount();
    }

    /**
     * 获取总共加载过的类数量
     */
    public static long getTotalLoadedClassCount() {
        ClassLoadingMXBean classLoadingMXBean = ManagementFactory.getClassLoadingMXBean();
        return classLoadingMXBean.getTotalLoadedClassCount();
    }

    /**
     * 格式化字节数为可读格式
     */
    public static String formatBytes(long bytes) {
        if (bytes < 1024) {
            return bytes + " B";
        }
        if (bytes < MB) {
            return DF.format((double) bytes / 1024) + " KB";
        }
        if (bytes < GB) {
            return DF.format((double) bytes / MB) + " MB";
        }
        return DF.format((double) bytes / GB) + " GB";
    }

    /**
     * 格式化时长为可读格式
     */
    public static String formatDuration(long millis) {
        long seconds = millis / 1000;
        long minutes = seconds / 60;
        long hours = minutes / 60;
        long days = hours / 24;

        if (days > 0) {
            return days + "天" + (hours % 24) + "小时";
        }
        if (hours > 0) {
            return hours + "小时" + (minutes % 60) + "分钟";
        }
        if (minutes > 0) {
            return minutes + "分钟" + (seconds % 60) + "秒";
        }
        return seconds + "秒";
    }

    /**
     * 获取系统完整信息
     */
    public static Map<String, Object> getFullSystemInfo() {
        Map<String, Object> info = new HashMap<>();

        info.put("cpuCoreCount", getCpuCoreCount());
        info.put("systemCpuLoad", DF.format(getSystemCpuLoad()) + "%");
        info.put("processCpuLoad", DF.format(getProcessCpuLoad()) + "%");

        info.put("totalMemory", getTotalMemoryMB() + "MB");
        info.put("freeMemory", getFreeMemoryMB() + "MB");
        info.put("usedMemory", getUsedMemoryMB() + "MB");
        info.put("memoryUsageRate", DF.format(getMemoryUsageRate()) + "%");

        info.put("jvmMaxMemory", getJvmMaxMemoryMB() + "MB");
        info.put("jvmTotalMemory", getJvmTotalMemoryMB() + "MB");
        info.put("jvmUsedMemory", getJvmUsedMemoryMB() + "MB");
        info.put("jvmMemoryUsageRate", DF.format(getJvmMemoryUsageRate()) + "%");

        info.put("diskTotalSpace", getDiskTotalSpaceGB() + "GB");
        info.put("diskFreeSpace", getDiskFreeSpaceGB() + "GB");
        info.put("diskUsedSpace", getDiskUsedSpaceGB() + "GB");
        info.put("diskUsageRate", DF.format(getDiskUsageRate()) + "%");

        info.put("osName", getOsName());
        info.put("osVersion", getOsVersion());
        info.put("osArch", getOsArch());

        info.put("javaVersion", getJavaVersion());
        info.put("javaHome", getJavaHome());
        info.put("jvmName", getJvmName());
        info.put("jvmVersion", getJvmVersion());
        info.put("jvmUptime", formatDuration(getJvmUptime()));

        info.put("threadCount", getThreadCount());
        info.put("daemonThreadCount", getDaemonThreadCount());
        info.put("peakThreadCount", getPeakThreadCount());

        info.put("loadedClassCount", getLoadedClassCount());
        info.put("unloadedClassCount", getUnloadedClassCount());
        info.put("totalLoadedClassCount", getTotalLoadedClassCount());

        return info;
    }
}
