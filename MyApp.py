import streamlit as st
import pandas as pd
import altair as alt
import calendar

@st.cache_data
def load_data():
    df = pd.read_excel('data3.xls')
    # Convert 'Fecha Documento' column to datetime format
    df['Fecha Documento'] = pd.to_datetime(df['Fecha Documento'], format='%d/%m/%Y')
    df = df.dropna(subset=['Sucursal'])
    return df


def main():
    df = load_data()
    st.title('Sales Dashboard: Con los últimos 3 meses de ventas')

    # Add date picker filter

    branches = st.multiselect(
        "Seleccione una Sucursal", df['Sucursal'].unique(), ["CASA MATRIZ"]
    )

    products = st.multiselect(
        "Seleccione un Producto or Servicio", df['Producto / Servicio'].unique(),
    )

    customers = st.multiselect(
    "Seleccione un Cliente (Opcional)", df['Cliente'].unique(),
    )

    if not branches:
        st.error("Por favor seleccione al menos un Sucursal.")
        st.stop()

     # Initialize the markdown string
    markdown_string = ""

    st.write("### Data de ventas para los filtros aplicados:")

    # Create a new DataFrame to hold sales data for all branches
    all_branches_monthly_sales = pd.DataFrame()

    for branch in branches:
        # Calculate total sales
        filtered_df = df[df['Sucursal'] == branch]
        total_branch = filtered_df['Subtotal Bruto'].sum()
        markdown_string += f"* **Ventas Totales {branch}:** ${total_branch:,.0f}\n"

        # Calculate total sales per month for the branch
        filtered_df = df[df['Sucursal'] == branch]
        monthly_sales = filtered_df.resample('M', on='Fecha Documento')['Subtotal Bruto'].sum()
        monthly_sales.name = branch  # Name the series after the branch
        monthly_sales.index = monthly_sales.index.strftime('%Y-%m')
        all_branches_monthly_sales = pd.concat([all_branches_monthly_sales, monthly_sales], axis=1).sort_index()


        for product in products:
            filtered_df = df[
                (df['Sucursal'] == branch) &
                (df['Producto / Servicio'] == product)
            ]
            total_product = filtered_df['Subtotal Bruto'].sum()
            markdown_string += f"    * **Ventas Totales {product} en {branch}:** ${total_product:,.0f}\n"
            for customer in customers:
                filtered_df = df[
                    (df['Sucursal'] == branch) &
                    (df['Producto / Servicio'] == product) &
                    (df['Cliente'] == customer)
                ]
                total_customer = filtered_df['Subtotal Bruto'].sum()
                markdown_string += f"        * **Ventas Totales {customer} en {product} en {branch}:** ${total_customer:,.0f}\n"

    # Display the markdown string
    st.markdown(markdown_string)
    # Charts by branch
    st.write("### Ventas Totales por Mes para todas las Sucursales seleccionadas:")
    st.bar_chart(all_branches_monthly_sales)

    # Filter the data
    filtered_df = df[
    (df['Sucursal'].isin(branches)) &
    (df['Cliente'].isin(customers) if customers else True) &
    (df['Producto / Servicio'].isin(products) if products else True)
    ]
    # st.write(f"Ventas Totales por Sucursal: {total_branch}")

    #Show data about the p

    # Visualize sales trends over time
    # Charts
    if not filtered_df.empty and products:
        chart_data = filtered_df.groupby(['Fecha Documento', 'Producto / Servicio'])['Subtotal Bruto'].sum().reset_index()

        chart = (
            alt.Chart(chart_data)
            .mark_point()
            .encode(
                x='Fecha Documento:T',
                y='Subtotal Bruto:Q',
                color='Producto / Servicio:N',
                tooltip=['Fecha Documento:T', 'Subtotal Bruto:Q']
            )
            + alt.Chart(chart_data)
            .mark_line()  # Connect the dots with lines
            .encode(
                x=alt.X('Fecha Documento:T', title='Fecha Documento'), # %B for full month name
                y=alt.Y('Subtotal Bruto:Q', title='Subtotal Bruto'), # No need to format here
                color='Producto / Servicio:N',
                # tooltip=['Fecha Documento:T', '(Subtotal Bruto):Q']
            )
            .properties(
                width=700,
                height=400,
                title='Tendencias de Ventas en el Tiempo filtros aplicados',
            )
        )

        st.altair_chart(chart, use_container_width=True)

    st.write(filtered_df)





    # Using object notation
    # add_selectbox = st.sidebar.selectbox(
    # "How would you like to be contacted?",
    # ("Email", "Home phone", "Mobile phone")
# )


if __name__ == '__main__':
    main()

#Filtro de tiempo
# CHECK Si no hay producto seleccionado mostrar grafica de ventas mensuales por sucursal CHECK
# Grafico seperado por sucursal en el que tiene todos los filtros
