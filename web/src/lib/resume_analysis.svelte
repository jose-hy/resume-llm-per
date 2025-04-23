<script lang="ts">
  import { marked } from "marked";
  import { onMount } from "svelte";

  import Spacer from "./spacer.svelte";
  import { backendURL } from "../utils";

  let isLoading = $state(false);

  const {
    improvement,
    disqualification,
    setImprovement,
    setDisqualification,
    description,
    file,
  } = $props();

  const getData = async (endpoint: string, formData: FormData) => {
    const res = await fetch(backendURL("/analyze/") + endpoint, {
      headers: {
        Accept: "application/json",
      },
      method: "POST",
      body: formData,
    });

    return await res.json();
  };

  onMount(async () => {
    if (improvement || disqualification) {
      return;
    }
    isLoading = true;

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", description);

    const [disqualificationData, improvementData] = await Promise.all([
      getData("disqualification", formData),
      getData("improvement", formData),
    ]);

    setDisqualification(disqualificationData.analysis);
    setImprovement(improvementData.analysis);
    isLoading = false;
  });
</script>

<div>
  {#if isLoading}
    <div class="flex items-center gap-2">
      <p>Analyzing resume</p>
      <div
        class="border-t-[black] border-l-[black] border-b-[black]
        w-[16px] h-[16px] border-[2px] border-transparent
        spinner animate-spin rounded-circle"
      ></div>
    </div>
  {:else}
    <p class="font-600 text-24px">Disqualifications</p>
    <Spacer size={8} axis="y" />
    {@html marked(disqualification)}
    <Spacer size={24} axis="y" />
    <p class="font-600 text-24px">Suggested improvements</p>
    <Spacer size={8} axis="y" />
    {@html marked(improvement)}
  {/if}
</div>
