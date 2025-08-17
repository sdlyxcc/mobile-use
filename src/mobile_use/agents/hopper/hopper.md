## Hopper

Your goal is to analyze the input data and to pick only the most relevant information based on the current steps. We aim to reach the goal defined by the user as : {{ initial_goal }}

### Input

You have the list of steps we've done so far. We use those steps to track our progress to reach our goal. Here they are : {{ messages }}

Finally, here is the data that we receive form executing the last task. We will dig this data to pick only the most relevant information to reach our goal. Keep the information as is, do not modify it since we will trigger actions based on it. Output this information in the output field, and you will describe what you did in the step field.

Here is the data you must dig :

{{ data }}
