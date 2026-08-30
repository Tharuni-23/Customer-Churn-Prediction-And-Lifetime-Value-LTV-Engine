import database as db


try:

    engine = db.get_engine()

    db.test_connection(engine)

    print("\nGetting customers...")

    customers = db.get_all_customers()

    print(
        "Number of customers:",
        len(customers)
    )

    print("\nFirst 5 customers:")

    print(
        customers.head()
    )

    print("\nDashboard summary:")

    summary = db.get_dashboard_summary()

    print(summary)

except Exception as e:

    print("\nERROR:")
    print(e)