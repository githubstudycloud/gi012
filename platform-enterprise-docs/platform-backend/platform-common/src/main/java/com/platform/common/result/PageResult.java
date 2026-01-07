package com.platform.common.result;

import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serial;
import java.util.Collections;
import java.util.List;

/**
 * 分页响应结果封装
 *
 * @param <T> 数据类型
 * @author Platform Team
 * @since 1.0.0
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class PageResult<T> extends Result<List<T>> {

    @Serial
    private static final long serialVersionUID = 1L;

    /**
     * 当前页码
     */
    private long pageNum;

    /**
     * 每页大小
     */
    private long pageSize;

    /**
     * 总记录数
     */
    private long total;

    /**
     * 总页数
     */
    private long pages;

    /**
     * 是否有下一页
     */
    private boolean hasNext;

    /**
     * 是否有上一页
     */
    private boolean hasPrevious;

    public PageResult() {
        super();
    }

    public PageResult(List<T> data, long pageNum, long pageSize, long total) {
        super(200, "操作成功", data);
        this.pageNum = pageNum;
        this.pageSize = pageSize;
        this.total = total;
        this.pages = pageSize > 0 ? (total + pageSize - 1) / pageSize : 0;
        this.hasNext = pageNum < this.pages;
        this.hasPrevious = pageNum > 1;
    }

    /**
     * 创建分页结果
     */
    public static <T> PageResult<T> of(List<T> data, long pageNum, long pageSize, long total) {
        return new PageResult<>(data, pageNum, pageSize, total);
    }

    /**
     * 创建空分页结果
     */
    public static <T> PageResult<T> empty(long pageNum, long pageSize) {
        return new PageResult<>(Collections.emptyList(), pageNum, pageSize, 0);
    }
}
