/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class FileUploadWidget extends Component {
    static template = "frontend_enhancement.FileUploadWidget";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.state = useState({
            files: [],
            isDragging: false,
            isUploading: false,
            uploadProgress: 0,
            userStats: null,
        });

        this.fileInputRef = useRef("fileInput");
        this.dropAreaRef = useRef("dropArea");

        onMounted(() => {
            this.loadUserStats();
            this.setupDragAndDrop();
        });
    }

    async loadUserStats() {
        try {
            const result = await this.rpc("/web/file_upload/get_user_stats", {});
            if (result.success) {
                this.state.userStats = result.stats;
            }
        } catch (error) {
            console.error("Failed to load user stats:", error);
        }
    }

    setupDragAndDrop() {
        const dropArea = this.dropAreaRef.el;
        if (!dropArea) return;

        // Prevent default drag behaviors
        ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
            dropArea.addEventListener(eventName, this.preventDefaults.bind(this));
            document.body.addEventListener(eventName, this.preventDefaults.bind(this));
        });

        // Highlight drop area when item is dragged over it
        ["dragenter", "dragover"].forEach((eventName) => {
            dropArea.addEventListener(eventName, () => {
                this.state.isDragging = true;
            });
        });

        ["dragleave", "drop"].forEach((eventName) => {
            dropArea.addEventListener(eventName, () => {
                this.state.isDragging = false;
            });
        });

        // Handle dropped files
        dropArea.addEventListener("drop", this.handleDrop.bind(this));
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        this.handleFiles(files);
    }

    onFileSelect() {
        const fileInput = this.fileInputRef.el;
        if (fileInput && fileInput.files) {
            this.handleFiles(fileInput.files);
        }
    }

    async handleFiles(files) {
        if (this.props.readonly) return;

        const fileArray = Array.from(files);

        // Validate files
        for (const file of fileArray) {
            const validation = await this.validateFile(file);
            if (!validation.success) {
                this.notification.add(validation.error, { type: "danger" });
                return;
            }
        }

        // Upload files
        this.state.isUploading = true;
        this.state.uploadProgress = 0;

        try {
            const uploadPromises = fileArray.map((file) => this.uploadFile(file));
            const results = await Promise.all(uploadPromises);

            const successful = results.filter((r) => r.success);
            const failed = results.filter((r) => !r.success);

            if (successful.length > 0) {
                this.notification.add(_t("Successfully uploaded %s file(s)", successful.length), { type: "success" });
                await this.loadUserStats();
                this.trigger("files-uploaded", { files: successful });
            }

            if (failed.length > 0) {
                this.notification.add(_t("Failed to upload %s file(s)", failed.length), { type: "warning" });
            }
        } catch (error) {
            this.notification.add(_t("Upload failed: %s", error.message), { type: "danger" });
        } finally {
            this.state.isUploading = false;
            this.state.uploadProgress = 0;
        }
    }

    async validateFile(file) {
        try {
            const result = await this.rpc("/web/file_upload/validate", {
                file_name: file.name,
                file_size: file.size,
                file_type: file.type,
            });
            return result;
        } catch (error) {
            return {
                success: false,
                error: _t("Validation failed: %s", error.message),
            };
        }
    }

    async uploadFile(file) {
        return new Promise((resolve) => {
            const reader = new FileReader();

            reader.onload = async (e) => {
                try {
                    const fileData = btoa(e.target.result);

                    const result = await this.rpc("/web/file_upload/create", {
                        file_data: fileData,
                        name: file.name,
                        description: "",
                        access_level: "internal",
                        related_model: this.props.record.resModel,
                        related_record_id: this.props.record.resId,
                    });

                    resolve(result);
                } catch (error) {
                    resolve({
                        success: false,
                        error: error.message,
                    });
                }
            };

            reader.onerror = () => {
                resolve({
                    success: false,
                    error: _t("Failed to read file"),
                });
            };

            reader.readAsBinaryString(file);
        });
    }

    onBrowseFiles() {
        if (this.props.readonly) return;
        const fileInput = this.fileInputRef.el;
        if (fileInput) {
            fileInput.click();
        }
    }

    getUploadAreaClass() {
        let classes = "o_file_upload_area";
        if (this.state.isDragging) {
            classes += " o_file_upload_dragging";
        }
        if (this.state.isUploading) {
            classes += " o_file_upload_uploading";
        }
        if (this.props.readonly) {
            classes += " o_file_upload_readonly";
        }
        return classes;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    }

    getFileTypeIcon(mimeType) {
        const iconMap = {
            "application/pdf": "fa-file-pdf-o",
            "application/msword": "fa-file-word-o",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "fa-file-word-o",
            "application/vnd.ms-excel": "fa-file-excel-o",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "fa-file-excel-o",
            "text/plain": "fa-file-text-o",
            "image/jpeg": "fa-file-image-o",
            "image/png": "fa-file-image-o",
            "image/gif": "fa-file-image-o",
            "application/zip": "fa-file-archive-o",
        };

        return iconMap[mimeType] || "fa-file-o";
    }
}

// QWeb Template
const fileUploadTemplate = `
<div class="o_file_upload_widget">
    <div t-ref="dropArea" t-att-class="getUploadAreaClass()" t-on-click="onBrowseFiles">
        <input t-ref="fileInput" type="file" multiple="true" 
               class="d-none" t-on-change="onFileSelect"/>
        
        <div class="o_upload_placeholder" t-if="!state.isUploading">
            <div class="text-center">
                <i class="fa fa-cloud-upload fa-3x text-muted mb-3"/>
                <h5 class="text-muted">
                    <t t-if="state.isDragging">Drop files here</t>
                    <t t-else="">Drag &amp; Drop files here</t>
                </h5>
                <p class="text-muted">
                    or <a href="#" class="text-primary">browse to select files</a>
                </p>
                <div t-if="state.userStats" class="small text-muted mt-2">
                    <div>Max size: <t t-esc="formatFileSize(state.userStats.max_upload_size)"/></div>
                    <div>Allowed types: <t t-esc="state.userStats.allowed_file_types.join(', ')"/></div>
                </div>
            </div>
        </div>
        
        <div class="o_upload_progress" t-if="state.isUploading">
            <div class="text-center">
                <i class="fa fa-spinner fa-spin fa-2x text-primary mb-3"/>
                <h5 class="text-primary">Uploading files...</h5>
                <div class="progress mb-2" style="height: 20px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" t-att-style="'width: ' + state.uploadProgress + '%'"
                         t-att-aria-valuenow="state.uploadProgress" aria-valuemin="0" aria-valuemax="100">
                        <t t-esc="state.uploadProgress"/>%
                    </div>
                </div>
                <p class="text-muted">Please wait while files are being uploaded...</p>
            </div>
        </div>
    </div>
    
    <div t-if="state.userStats" class="o_upload_stats mt-3">
        <div class="row text-center">
            <div class="col-3">
                <div class="o_stat_card">
                    <div class="o_stat_number text-primary">
                        <t t-esc="state.userStats.total_files"/>
                    </div>
                    <div class="o_stat_label">Total Files</div>
                </div>
            </div>
            <div class="col-3">
                <div class="o_stat_card">
                    <div class="o_stat_number text-success">
                        <t t-esc="formatFileSize(state.userStats.total_size)"/>
                    </div>
                    <div class="o_stat_label">Total Size</div>
                </div>
            </div>
            <div class="col-3">
                <div class="o_stat_card">
                    <div class="o_stat_number text-info">
                        <t t-esc="state.userStats.total_downloads"/>
                    </div>
                    <div class="o_stat_label">Downloads</div>
                </div>
            </div>
            <div class="col-3">
                <div class="o_stat_card">
                    <div class="o_stat_number text-warning">
                        <t t-esc="formatFileSize(state.userStats.average_size)"/>
                    </div>
                    <div class="o_stat_label">Avg Size</div>
                </div>
            </div>
        </div>
    </div>
</div>
`;

registry.category("fields").add("file_upload_widget", FileUploadWidget);

// Register template
registry.category("templates").add("frontend_enhancement.FileUploadWidget", fileUploadTemplate);
