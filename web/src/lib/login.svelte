<script lang="ts">
  import { goto, invalidateAll } from "$app/navigation";
  import { formFunc } from "./loginForm.svelte.js";
  import { supabase } from "./supabaseClient.js";
  import * as v from "valibot";
  import Spacer from "./spacer.svelte";
  //import { ActionData, SubmitFunction } from './$types.js';

  const { sessionID } = $props();

  export const form = formFunc({
    email: v.pipe(v.string(), v.nonEmpty("Email is required"),
    v.email("Invalid email")),
    password: v.pipe(
      v.string(), v.nonEmpty("Password is required"),
      v.minLength(6, "Password must be at least 6 characters long"),
    ),
  });

  let email = $state("");
  let status = $state("sign in");
  let password = $state("");
  let confirmPassword = $state("");
  let isLoading = $state(false);
  let errorMsg = $state("");
  // Stops button click when email/password is empty
  let isEmpty = $derived(email === "" || password === "");

  const register = async () => {
    errorMsg = "";
      if (form.validate({ email, password }) && confirmPassword === password) {
        isLoading = true;
        try {
          const { data, error } = await supabase.auth.signUp({ email: email, password: password});
          //console.log("Supabase signUp response:", { data, error });
        } catch (err) {
          console.log(err);
          isLoading = false;
        }
      }
      await invalidateAll();
      isLoading = false;
  };

  const login = async () => {
    isLoading = true;
    errorMsg = "";
    if (isEmpty) {
      isLoading = false;
      return;
    }
    try {
      const { data: signIn, error: signErr} = await supabase.auth.signInWithPassword({ email: email, password: password });
      //console.log("Supabase signIn response:", signIn);
      if (signErr) {
        errorMsg = "Incorrect username or password.";
        throw signErr;
      }
      // Send analytics event for daily active user
      const statusError = await supabase.from("analytics").insert({
        user_id: signIn.user?.id || "",
        type: "daily_active_user",
        data: {
          count: 1,
          session_id: sessionID,
        }
      })
      goto("/registration");
    } catch (err) {
      isLoading = false;
      errorMsg = "Incorrect username or password.";
      console.log(err);
      await invalidateAll();
    }
  };
</script>

<div class="h-[100vh] grid place-content-center">
  <form
    class="bg-white px-20px py-24px rounded-[10px] [border:1px_solid_#DADADA]
    w-[90vw] max-w-[400px] flex flex-col items-center"
  >
    <h1 class="text-center font-700 text-24px">Interview Moves</h1>
    <Spacer axis="y" size={24} />
    <div class="flex flex-col gap-4px w-full">
      <label class="font-600 text-15px" for="email">Email</label>
      <input
        class="[border:1px_solid_#DADADA] rounded-4px px-8px py-[6px]"
        bind:value={email}
        id="email"
      />
    </div>
    <p>{form.errors.email}</p>
    <Spacer axis="y" size={20} />
    <div class="flex flex-col gap-4px w-full">
      <label class="font-600 text-15px" for="password">Password</label>
      <input
        class="[border:1px_solid_#DADADA] rounded-4px px-8px py-[6px]"
        bind:value={password}
        id="password"
        type="password"
      />
    </div>
    <p>{form.errors.password}</p>
    <Spacer axis="y" size={20} />
    {#if status === "sign up" }
      <div class="flex flex-col gap-4px w-full">
      <label class="font-600 text-15px" for="confirmPassword">Confirm Password</label>
      <input
        class="[border:1px_solid_#DADADA] rounded-4px px-8px py-[6px]"
        bind:value={confirmPassword}
        id="confirmPassword"
        type="password"
      />
    </div>
    {/if}
    {#if errorMsg}
      <div class="text-red-600 mb-2">{errorMsg}</div>
    {/if}
    <Spacer axis="y" size={20} />
    <button
      class="bg-black text-white rounded-8px px-12px py-8px w-full mx-auto
      flex items-center gap-4 justify-center"
      onclick={status === "sign in" ? login : register}
    >
      {status === "sign in" ? "Sign in" : "Register"}
      {#if isLoading}
        <div
          class="border-t-[white] border-l-[white] border-b-[white]
        w-[16px] h-[16px] border-[2px] border-transparent
        spinner animate-spin rounded-circle"
        ></div>
      {/if}
    </button>
    <Spacer axis="y" size={24} />
    {#if status === "sign in"}
      <span class="">
        Need an account?
        <button class="font-600" onclick={() => (status = "sign up")}>
          Sign up
        </button>
      </span>
    {:else}
      <span>
        Have an account?
        <button class="font-600" onclick={() => (status = "sign in")}>
          Sign in
        </button>
      </span>
    {/if}
  </form>
</div>
