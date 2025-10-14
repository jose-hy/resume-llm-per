import * as v from "valibot";

export function formFunc<T extends Record<string, v.BaseSchema<any, any, any>>>(
  schema: T
) {
  const LoginSchema = v.object(schema);

  type LoginData = v.InferOutput<typeof LoginSchema>;

  const errObj: Record<keyof T, string> = {} as Record<keyof T, string>;

  for (const k in schema) {
    errObj[k] = "";
  }

  let errors = $state(errObj);

  return {
    get errors() {
      return errors;
    },
    validate: (data: LoginData) => {
      const parsed = v.safeParse(LoginSchema, {
        email: data.email,
        password: data.password,
      });

      if (!parsed.success) {
        for (const issue of parsed.issues ?? []) {
          if ("path" in issue) {
            for (const p of issue.path ?? []) {
              if (typeof p.key === "string") {
                errors[p.key as keyof T] = issue.message;
              }
            }
          }
        }
        console.log("This is an error: ", errors);
      }

      return parsed.success;
    },
  };
}
