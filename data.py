import streamlit as st
import snowflake.connector
import os
 
# --- Setup your Snowflake connection ---
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.getenv("SF_USER"),
        password=os.getenv("SF_PASSWORD"),
        account=os.getenv("SF_ACCOUNT"),
        role=os.getenv("SF_ROLE"),
        warehouse=os.getenv("SF_WAREHOUSE"),
        database=os.getenv("SF_DATABASE"),
        schema=os.getenv("SF_SCHEMA"),
    )
 
# --- Fetch list of users or roles ---
def fetch_list(query):
    conn = get_snowflake_connection()
    cs = conn.cursor()
    try:
        cs.execute(query)
        return [row[0] for row in cs.fetchall()]
    finally:
        cs.close()
        conn.close()
 
# --- Grant execution ---
def execute_grant(query):
    conn = get_snowflake_connection()
    cs = conn.cursor()
    try:
        cs.execute(query)
        return True, f"Executed: {query}"
    except Exception as e:
        return False, str(e)
    finally:
        cs.close()
        conn.close()
 
# --- Streamlit UI ---
st.title("Snowflake Grant Tool")
 
grant_type = st.selectbox("Grant to:", ["User", "Role"])
target = st.selectbox("Grant what?", ["Role", "Database", "Warehouse"])
 
if grant_type == "User":
    grantee_list = fetch_list("SHOW USERS")
else:
    grantee_list = fetch_list("SHOW ROLES")
 
grantee = st.selectbox("Select User/Role", grantee_list)
 
if target == "Role":
    item_list = fetch_list("SHOW ROLES")
elif target == "Database":
    item_list = fetch_list("SHOW DATABASES")
elif target == "Warehouse":
    item_list = fetch_list("SHOW WAREHOUSES")
 
item_to_grant = st.selectbox(f"Select {target}", item_list)
 
# Optional privileges
if target == "Role":
    privilege = "USAGE"
else:
    privilege = st.selectbox("Select Privilege", ["USAGE", "READ", "OPERATE"])
 
if st.button("Grant Now"):
    if target == "Role":
        query = f"GRANT ROLE {item_to_grant} TO {grant_type.upper()} {grantee}"
    else:
        query = f"GRANT {privilege} ON {target.upper()} {item_to_grant} TO {grant_type.upper()} {grantee}"
    
    success, message = execute_grant(query)
    if success:
        st.success(message)
    else:
        st.error(message)
