package com.example.utils;

import javax.servlet.http.HttpServletRequest;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.UnknownHostException;
import java.util.Enumeration;
import java.util.regex.Pattern;

/**
 * IP工具类
 * 提供IP地址相关的常用操作
 *
 * @author system
 * @date 2025-12-30
 */
public class IpUtil {

    private static final String UNKNOWN = "unknown";
    private static final String LOCALHOST_IPV4 = "127.0.0.1";
    private static final String LOCALHOST_IPV6 = "0:0:0:0:0:0:0:1";
    private static final String IP_SEPARATOR = ",";
    private static final int IP_MAX_LENGTH = 15;

    private static final Pattern IPV4_PATTERN = Pattern.compile(
        "^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\." +
        "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\." +
        "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\." +
        "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    );

    /**
     * 获取客户端真实IP地址
     * 支持通过代理、负载均衡等方式访问
     */
    public static String getRealIp(HttpServletRequest request) {
        if (request == null) {
            return LOCALHOST_IPV4;
        }

        String ip = getIpFromHeader(request, "X-Forwarded-For");
        if (isValidIp(ip)) {
            return getFirstIp(ip);
        }

        ip = getIpFromHeader(request, "X-Real-IP");
        if (isValidIp(ip)) {
            return ip;
        }

        ip = getIpFromHeader(request, "Proxy-Client-IP");
        if (isValidIp(ip)) {
            return ip;
        }

        ip = getIpFromHeader(request, "WL-Proxy-Client-IP");
        if (isValidIp(ip)) {
            return ip;
        }

        ip = request.getRemoteAddr();
        return normalizeLocalhost(ip);
    }

    /**
     * 从请求头获取IP
     */
    private static String getIpFromHeader(HttpServletRequest request, String headerName) {
        String ip = request.getHeader(headerName);
        return (ip != null && ip.length() > 0) ? ip : null;
    }

    /**
     * 获取第一个有效IP
     * X-Forwarded-For可能包含多个IP,格式: clientIP, proxy1IP, proxy2IP
     */
    private static String getFirstIp(String ips) {
        if (ips == null || ips.isEmpty()) {
            return LOCALHOST_IPV4;
        }

        String[] ipArray = ips.split(IP_SEPARATOR);
        for (String ip : ipArray) {
            String trimmedIp = ip.trim();
            if (isValidIp(trimmedIp)) {
                return trimmedIp;
            }
        }
        return LOCALHOST_IPV4;
    }

    /**
     * 验证IP是否有效
     */
    private static boolean isValidIp(String ip) {
        if (ip == null || ip.isEmpty()) {
            return false;
        }
        if (UNKNOWN.equalsIgnoreCase(ip)) {
            return false;
        }
        return ip.length() <= IP_MAX_LENGTH;
    }

    /**
     * 标准化localhost地址
     */
    private static String normalizeLocalhost(String ip) {
        if (LOCALHOST_IPV6.equals(ip)) {
            return LOCALHOST_IPV4;
        }
        return ip;
    }

    /**
     * 判断是否为有效的IPv4地址
     */
    public static boolean isValidIPv4(String ip) {
        if (ip == null || ip.isEmpty()) {
            return false;
        }
        return IPV4_PATTERN.matcher(ip).matches();
    }

    /**
     * 将IPv4地址转换为长整型
     */
    public static long ipToLong(String ip) {
        if (!isValidIPv4(ip)) {
            return 0L;
        }

        String[] segments = ip.split("\\.");
        long result = 0L;

        for (int i = 0; i < 4; i++) {
            long segment = Long.parseLong(segments[i]);
            result = (result << 8) | segment;
        }

        return result;
    }

    /**
     * 将长整型转换为IPv4地址
     */
    public static String longToIp(long ipLong) {
        if (ipLong < 0 || ipLong > 0xFFFFFFFFL) {
            return LOCALHOST_IPV4;
        }

        StringBuilder sb = new StringBuilder();
        sb.append((ipLong >> 24) & 0xFF).append(".");
        sb.append((ipLong >> 16) & 0xFF).append(".");
        sb.append((ipLong >> 8) & 0xFF).append(".");
        sb.append(ipLong & 0xFF);

        return sb.toString();
    }

    /**
     * 判断是否为内网IP
     */
    public static boolean isInternalIp(String ip) {
        if (!isValidIPv4(ip)) {
            return false;
        }

        if (isLoopbackIp(ip)) {
            return true;
        }

        long ipLong = ipToLong(ip);

        // 10.0.0.0 - 10.255.255.255
        long aBegin = ipToLong("10.0.0.0");
        long aEnd = ipToLong("10.255.255.255");
        if (ipLong >= aBegin && ipLong <= aEnd) {
            return true;
        }

        // 172.16.0.0 - 172.31.255.255
        long bBegin = ipToLong("172.16.0.0");
        long bEnd = ipToLong("172.31.255.255");
        if (ipLong >= bBegin && ipLong <= bEnd) {
            return true;
        }

        // 192.168.0.0 - 192.168.255.255
        long cBegin = ipToLong("192.168.0.0");
        long cEnd = ipToLong("192.168.255.255");
        return ipLong >= cBegin && ipLong <= cEnd;
    }

    /**
     * 判断是否为回环地址
     */
    public static boolean isLoopbackIp(String ip) {
        if (ip == null || ip.isEmpty()) {
            return false;
        }
        return LOCALHOST_IPV4.equals(ip) || LOCALHOST_IPV6.equals(ip);
    }

    /**
     * 获取本机IP地址
     */
    public static String getLocalIp() {
        try {
            InetAddress localHost = InetAddress.getLocalHost();
            String ip = localHost.getHostAddress();
            return normalizeLocalhost(ip);
        } catch (UnknownHostException e) {
            return LOCALHOST_IPV4;
        }
    }

    /**
     * 获取本机实际网卡IP地址(非回环地址)
     */
    public static String getActualLocalIp() {
        try {
            Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
            while (interfaces.hasMoreElements()) {
                NetworkInterface ni = interfaces.nextElement();
                if (shouldSkipInterface(ni)) {
                    continue;
                }

                String ip = getValidIpFromInterface(ni);
                if (ip != null) {
                    return ip;
                }
            }
        } catch (Exception e) {
            return LOCALHOST_IPV4;
        }
        return LOCALHOST_IPV4;
    }

    /**
     * 判断是否应该跳过该网卡接口
     */
    private static boolean shouldSkipInterface(NetworkInterface ni) {
        try {
            if (ni.isLoopback() || ni.isVirtual() || !ni.isUp()) {
                return true;
            }
        } catch (Exception e) {
            return true;
        }
        return false;
    }

    /**
     * 从网卡接口获取有效IP
     */
    private static String getValidIpFromInterface(NetworkInterface ni) {
        Enumeration<InetAddress> addresses = ni.getInetAddresses();
        while (addresses.hasMoreElements()) {
            InetAddress addr = addresses.nextElement();
            if (isValidLocalAddress(addr)) {
                return addr.getHostAddress();
            }
        }
        return null;
    }

    /**
     * 判断是否为有效的本地地址
     */
    private static boolean isValidLocalAddress(InetAddress addr) {
        if (addr.isLoopbackAddress() || addr.isAnyLocalAddress()) {
            return false;
        }

        String ip = addr.getHostAddress();
        return isValidIPv4(ip) && !isLoopbackIp(ip);
    }

    /**
     * 获取IP所在网段
     */
    public static String getIpSegment(String ip, int maskBits) {
        if (!isValidIPv4(ip) || maskBits < 0 || maskBits > 32) {
            return null;
        }

        long ipLong = ipToLong(ip);
        long mask = createMask(maskBits);
        long networkAddress = ipLong & mask;

        return longToIp(networkAddress);
    }

    /**
     * 创建子网掩码
     */
    private static long createMask(int maskBits) {
        if (maskBits == 0) {
            return 0L;
        }
        return (0xFFFFFFFFL << (32 - maskBits)) & 0xFFFFFFFFL;
    }

    /**
     * 判断IP是否在指定网段内
     */
    public static boolean isInRange(String ip, String networkIp, int maskBits) {
        if (!isValidIPv4(ip) || !isValidIPv4(networkIp)) {
            return false;
        }

        String ipSegment = getIpSegment(ip, maskBits);
        String networkSegment = getIpSegment(networkIp, maskBits);

        return ipSegment != null && ipSegment.equals(networkSegment);
    }
}
