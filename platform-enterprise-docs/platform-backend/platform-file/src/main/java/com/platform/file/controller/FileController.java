package com.platform.file.controller;

import com.platform.common.result.Result;
import com.platform.file.service.FileService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

/**
 * 文件管理控制器
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Tag(name = "文件管理", description = "文件上传、下载、删除")
@RestController
@RequestMapping("/files")
@RequiredArgsConstructor
public class FileController {

    private final FileService fileService;

    @Operation(summary = "上传文件")
    @PostMapping("/upload")
    public Result<String> upload(@Parameter(description = "文件") @RequestParam("file") MultipartFile file) {
        String objectName = fileService.upload(file);
        return Result.success(objectName);
    }

    @Operation(summary = "下载文件")
    @GetMapping("/download/{*objectName}")
    public ResponseEntity<InputStreamResource> download(
            @Parameter(description = "对象名称") @PathVariable String objectName) {
        InputStream inputStream = fileService.download(objectName);
        String filename = objectName.substring(objectName.lastIndexOf("/") + 1);
        String encodedFilename = URLEncoder.encode(filename, StandardCharsets.UTF_8);

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + encodedFilename + "\"")
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .body(new InputStreamResource(inputStream));
    }

    @Operation(summary = "获取文件预签名URL")
    @GetMapping("/presigned-url")
    public Result<String> getPresignedUrl(
            @Parameter(description = "对象名称") @RequestParam String objectName,
            @Parameter(description = "过期时间（分钟）") @RequestParam(defaultValue = "60") int expireMinutes) {
        String url = fileService.getPresignedUrl(objectName, expireMinutes);
        return Result.success(url);
    }

    @Operation(summary = "删除文件")
    @DeleteMapping("/{*objectName}")
    public Result<Void> delete(@Parameter(description = "对象名称") @PathVariable String objectName) {
        fileService.delete(objectName);
        return Result.success();
    }
}
