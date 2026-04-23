<script lang="ts">
  import Transition from "svelte-transition";
  import Spacer from "./spacer.svelte";
  import { supabase } from "./supabaseClient.js";

  const { userID, job_id, title, company, location, description, apply_link, is_remote, dialog } = $props();

  const handleAppliedToJob = async () => {
    dialog.close();
    const { data, error } = await supabase.from("applied_to").upsert(
      {
        user_id: userID, 
        job_id: job_id, 
        title: title, 
        company: company,
        location: location, 
        description: description,
        apply_link: apply_link,
        created_at: new Date().toISOString(),
        is_remote: is_remote,
        applied_to_count: 1,
      });
    if (error) {
      console.error("Error applying to job:", error);
    }
  };
</script>

<div class="relative z-10">
  <Transition show={$dialog.expanded}>
    <Transition
      enter="ease-out duration-300"
      enterFrom="opacity-0"
      enterTo="opacity-100"
      leave="ease-in duration-200"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
    >
      <button
        class="fixed inset-0 bg-black bg-opacity-25"
        onclick={dialog.close}
      >
        close
      </button>
    </Transition>

    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4 text-center">
        <Transition
          enterFrom="opacity-0 scale-95"
          enter="ease-out duration-300"
          enterTo="opacity-100 scale-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100 scale-100"
          leaveTo="opacity-0 scale-95"
        >
          <div
            class="w-full max-w-[500px] transform overflow-hidden rounded-12px
              bg-white p-6 text-left align-middle shadow-xl transition-all"
            use:dialog.modal
          >
            <p class="text-[18px] font-500 align-middle text-center">
              Did you apply to <span class="font-700 text-[18px]">
                {title}
              </span>?
            </p>
            <Spacer size={16} axis="y" />
            <div class="flex gap-2 align-middle justify-center">
              <button
                onclick={handleAppliedToJob}
                class="bg-black text-white rounded-4px px-12px py-4px h-full min-w-[72px]"
              >
                Yes
              </button>
              <button
                onclick={dialog.close}
                class="[border:1px_solid_black] rounded-4px px-12px py-4px min-w-[72px]"
              >
                No
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </Transition>
</div>
