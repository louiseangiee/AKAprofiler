<template>
    <div>
        <div class="relative flex flex-wrap mt-4">
            <div>
            <h1 class="text-3xl font-semibold text-white">Upload PDF Files</h1>
            <p class="mt-2 text-sm text-blueGray-200">Upload Your Case Files Here</p>
            </div>
            <!-- Upload multiple PDF files -->
            <div class="w-full lg:w-12 pb-4 mt-10">
                <FileInput @change="uploadFiles" />
            </div>
        </div>
        <!-- Toasts -->
        <div class="relative bottom-0 right-0 z-50 flex items-end justify-end w-full h-full py-6">
            <!-- Success Toast -->
            <div
                v-if="showSuccessToast"
                id="toast-success"
                class="fixed flex items-center max-w-xs p-4 space-x-4 text-gray-500 bg-white divide-gray-200 rounded-lg shadow-sm right-5 bottom-1 dark:text-gray-400 dark:divide-gray-700 dark:bg-gray-800 divide-x rtl:divide-x-reverse"
                role="alert"
            >
                <div class="inline-flex items-center justify-center shrink-0 w-5 h-5 text-emerald-400 bg-emerald-400 rounded-lg dark:bg-emerald-800 dark:emerald-200">
                    <svg
                    class="w-3 h-3"
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    >
                    <path
                        d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 8.207-4 4a1 1 0 0 1-1.414 0l-2-2a1 1 0 0 1 1.414-1.414L9 10.586l3.293-3.293a1 1 0 0 1 1.414 1.414Z"
                    />
                    </svg>
                    <span class="sr-only">Check icon</span>
                </div>
                <div class="ms-3 text-sm font-normal">{{ successMessage }}</div>
                <button
                    type="button"
                    @click="showSuccessToast = false"
                    class="ms-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex items-center justify-center h-5 w-5 dark:text-gray-500 dark:hover:text-white dark:bg-gray-800 dark:hover:bg-gray-700"
                    aria-label="Close"
                >
                    <span class="sr-only">Close</span>
                    <svg
                    class="w-2 h-2"
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 14 14"
                    >
                        <path
                            stroke="currentColor"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
                        />
                    </svg>
                </button>
            </div>

            <!-- Error Toast -->
            <div
                v-if="showErrorToast"
                id="toast-danger"
                class="fixed right-5 bottom-6 flex items-center max-w-xs p-4 space-x-4 text-gray-500 bg-white divide-gray-200 rounded-lg shadow-sm  dark:text-gray-400 dark:divide-gray-700 dark:bg-gray-800 divide-x rtl:divide-x-reverse mt-6"
                role="alert"
                >
                <div class="inline-flex items-center justify-center shrink-0 w-5 h-5 text-red-500 bg-red-100 rounded-lg dark:bg-red-800 dark:text-red-200">
                    <svg
                    class="w-3 h-3"
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    >
                    <path
                        d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 11.793a1 1 0 1 1-1.414 1.414L10 11.414l-2.293 2.293a1 1 0 0 1-1.414-1.414L8.586 10 6.293 7.707a1 1 0 0 1 1.414-1.414L10 8.586l2.293-2.293a1 1 0 0 1 1.414 1.414L11.414 10l2.293 2.293Z"
                    />
                    </svg>
                    <span class="sr-only">Error icon</span>
                </div>
                <div class="ms-3 text-sm font-normal">{{ errorMessage }}</div>
                <button
                    type="button"
                    @click="showErrorToast = false"
                    class="ms-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex items-center justify-center h-5 w-5 dark:text-gray-500 dark:hover:text-white dark:bg-gray-800 dark:hover:bg-gray-700"
                    aria-label="Close"
                >
                    <span class="sr-only">Close</span>
                    <svg
                        class="w-2 h-2"
                        aria-hidden="true"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 14 14"
                    >
                        <path
                            stroke="currentColor"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
                        />
                    </svg>
                </button>
            </div>
        </div>
    </div>

</template>

<script>
import FileInput from "@/components/Input/FileInput.vue";
import axios from "axios";

export default {
    components: {
        FileInput
    },
    data() {
        return {
        showSuccessToast: false,
        showErrorToast: false,
        successMessage: "",
        errorMessage: "",
        };
    },
    methods: {
        uploadFiles(e) {
            // e is the event object coming from FileInput
            const files = e.target.files;
            console.log("Files selected:", files);
            
            // Create a FormData instance and append each file using the key "file"
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append("file", files[i]);
            }

            // Send a POST request to the /upload endpoint
            // Adjust the URL if your backend is on a different origin or port.
            axios.post("http://127.0.0.1:5000/upload", formData, {
                headers: {
                "Content-Type": "multipart/form-data"
                }
            })
            .then(response => {
                console.log("Upload successful:", response.data);
                // You can add additional logic here to update your UI.
                this.successMessage = "Files uploaded successfully.";
                this.showSuccessToast = true;
                // Automatically hide the success toast after 3 seconds.
                setTimeout(() => {
                    this.showSuccessToast = false;
                }, 3000);
            })
            .catch(error => {
                console.error("Upload failed:", error);
                this.errorMessage = "Upload failed. Please try again.";
                this.showErrorToast = true;
                // Automatically hide the error toast after 3 seconds.
                setTimeout(() => {
                    this.showErrorToast = false;
                }, 3000);
            });
        }
    }
}
</script>