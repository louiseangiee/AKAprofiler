<template>
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
</template>

<script>
import FileInput from "@/components/Input/FileInput.vue";

export default {
    components: {
        FileInput
    },
    methods: {
        uploadFiles(e) {
            console.log(e.target.files);
        }
    }
}
</script>