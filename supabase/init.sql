-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Recipe History table
create table recipe_history (
    id uuid default uuid_generate_v4() primary key,
    user_id text not null,
    ingredients jsonb,
    dietary_restrictions jsonb,
    recipes jsonb,
    meal_plan jsonb,
    grocery_list jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create index on user_id for faster queries
create index recipe_history_user_id_idx on recipe_history(user_id);

-- Favorite Recipes table
create table favorite_recipes (
    id uuid default uuid_generate_v4() primary key,
    user_id text not null,
    recipe_id text not null,
    recipe_name text,
    recipe_instructions text,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    unique(user_id, recipe_id)
);

-- Create index on user_id for faster queries
create index favorite_recipes_user_id_idx on favorite_recipes(user_id);

-- Enable Row Level Security (RLS)
alter table recipe_history enable row level security;
alter table favorite_recipes enable row level security;

-- Create policies
create policy "Users can view their own recipe history"
    on recipe_history for select
    using (auth.uid()::text = user_id);

create policy "Users can insert their own recipe history"
    on recipe_history for insert
    with check (auth.uid()::text = user_id);

create policy "Users can view their own favorite recipes"
    on favorite_recipes for select
    using (auth.uid()::text = user_id);

create policy "Users can manage their own favorite recipes"
    on favorite_recipes for all
    using (auth.uid()::text = user_id); 