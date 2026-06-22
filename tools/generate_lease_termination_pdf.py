#!/usr/bin/env python3
"""Generate the Mutual Lease Termination Agreement and Release PDF."""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = "renders/Mutual_Lease_Termination_Agreement.pdf"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetaLine",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Cell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CellRight",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            alignment=2,  # right
        )
    )
    styles.add(
        ParagraphStyle(
            name="CellBoldRight",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            alignment=2,
        )
    )
    return styles


def build_story(styles):
    story = []

    story.append(
        Paragraph("MUTUAL LEASE TERMINATION AGREEMENT AND RELEASE", styles["DocTitle"])
    )
    story.append(
        Paragraph("PROPERTY ADDRESS: 8220 Hawthorne Ave, Miami, FL 33141", styles["MetaLine"])
    )
    story.append(Paragraph("ORIGINAL LEASE DATE: October 19, 2025", styles["MetaLine"]))
    story.append(
        Paragraph("EFFECTIVE TERMINATION DATE: July 2, 2026", styles["MetaLine"])
    )
    story.append(Spacer(1, 16))

    story.append(
        Paragraph(
            "This Mutual Lease Termination Agreement (&ldquo;Agreement&rdquo;) is entered into this "
            "22nd day of June, 2026, by and between the following parties:",
            styles["Body"],
        )
    )
    story.append(Paragraph("<b>LANDLORD:</b> Harry Sitbon", styles["Body"]))
    story.append(
        Paragraph("<b>TENANTS:</b> Zachary Murray &amp; Stephen Hakami-Yazdy", styles["Body"])
    )

    story.append(
        Paragraph(
            "WHEREAS, Landlord and Tenants are parties to a residential lease agreement for the "
            "property located at 8220 Hawthorne Ave, Miami, FL 33141, which was originally scheduled "
            "to expire on October 31, 2026; and",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            "WHEREAS, the parties have mutually agreed to terminate the lease early, effective at "
            "11:59 PM on July 2, 2026;",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            "NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties "
            "agree as follows:",
            styles["Body"],
        )
    )

    # Section 1
    story.append(Paragraph("1. SURRENDER OF PREMISES", styles["SectionHeading"]))
    story.append(
        Paragraph(
            "The Tenants agree to completely vacate the property, remove all personal items, and "
            "return all two (2) sets of dwelling keys and one (1) mailbox key to the Landlord on or "
            "before July 2, 2026.",
            styles["Body"],
        )
    )

    # Section 2
    story.append(
        Paragraph("2. FINANCIAL RECONCILIATION &amp; ACCOUNTING", styles["SectionHeading"])
    )
    story.append(
        Paragraph(
            "The parties agree that the net balance due to the Tenants is calculated as follows:",
            styles["Body"],
        )
    )

    table_data = [
        [
            Paragraph("Item Description", styles["CellBold"]),
            Paragraph("Financial Calculation", styles["CellBold"]),
            Paragraph("Balance", styles["CellBoldRight"]),
        ],
        [
            Paragraph("Last Month's Rent Deposit", styles["Cell"]),
            Paragraph("Credited back to Tenant", styles["Cell"]),
            Paragraph("+$15,000.00", styles["CellRight"]),
        ],
        [
            Paragraph("Security Deposit", styles["Cell"]),
            Paragraph("Held by Landlord pending inspection", styles["Cell"]),
            Paragraph("+$15,000.00", styles["CellRight"]),
        ],
        [
            Paragraph("July Occupancy Adjustment", styles["Cell"]),
            Paragraph("Prorated rent (2 days @ $500.00/day)", styles["Cell"]),
            Paragraph("-$1,000.00", styles["CellRight"]),
        ],
        [
            Paragraph("NET BALANCE DUE TO TENANTS", styles["CellBold"]),
            Paragraph("Payable per the schedule below", styles["Cell"]),
            Paragraph("+$29,000.00", styles["CellBoldRight"]),
        ],
    ]

    table = Table(table_data, colWidths=[2.5 * inch, 2.6 * inch, 1.4 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#888888")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef2f5")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f7f9fa")]),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "The net balance of $29,000.00 shall be disbursed to the Tenants in two (2) "
            "installments as set forth below:",
            styles["Body"],
        )
    )

    schedule_data = [
        [
            Paragraph("Installment", styles["CellBold"]),
            Paragraph("Payment Condition / Timing", styles["CellBold"]),
            Paragraph("Amount", styles["CellBoldRight"]),
        ],
        [
            Paragraph("First Installment", styles["Cell"]),
            Paragraph("Due upon execution (signing) of this Agreement", styles["Cell"]),
            Paragraph("$15,000.00", styles["CellRight"]),
        ],
        [
            Paragraph("Second Installment", styles["Cell"]),
            Paragraph(
                "Due no later than three (3) business days following the move-out walkthrough "
                "inspection and the Tenants' full surrender of the premises (net of the $1,000.00 "
                "July occupancy adjustment)",
                styles["Cell"],
            ),
            Paragraph("$14,000.00", styles["CellRight"]),
        ],
        [
            Paragraph("TOTAL DISBURSEMENT", styles["CellBold"]),
            Paragraph("", styles["Cell"]),
            Paragraph("$29,000.00", styles["CellBoldRight"]),
        ],
    ]

    schedule = Table(schedule_data, colWidths=[1.5 * inch, 3.6 * inch, 1.4 * inch])
    schedule.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#888888")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef2f5")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f7f9fa")]),
            ]
        )
    )
    story.append(schedule)
    story.append(Spacer(1, 10))

    # Section 3
    story.append(
        Paragraph("3. MOVE-OUT INSPECTION &amp; DEPOSIT DEDUCTIONS", styles["SectionHeading"])
    )
    story.append(
        Paragraph(
            "The $15,000.00 first installment shall be paid upon execution of this Agreement and is "
            "not contingent upon the inspection. A physical move-out walkthrough inspection shall be "
            "conducted, the results of which shall apply solely to determining documented damage "
            "deductions from the $14,000.00 second installment and shall not affect the termination "
            "or the mutual release set forth in Section 4. The second installment, net of the "
            "$1,000.00 July occupancy adjustment, shall be paid to the Tenants no later than three "
            "(3) business days following the move-out walkthrough inspection.",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            "Any deduction from the second installment shall be limited to the documented cost of "
            "repairing damage beyond normal wear and tear, or replacing missing items, itemized in "
            "writing in accordance with Florida Statute &sect; 83.49(3). The parties acknowledge "
            "that the original lease did not list any furniture or appliances (Section 2 was left "
            "blank), and no inventory of furnishings shall serve as a basis for any deduction.",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            "The Tenants shall not be charged, and no deduction shall be made, for any condition "
            "existing prior to move-out or caused by the Landlord or the property's ongoing "
            "defects, including without limitation: water intrusion and water damage; mold and any "
            "humidity- or moisture-related damage; the open or unsealed drywall at the front "
            "entrance; damage arising from the roof leaks and related repairs; termite, cockroach, "
            "or other pest activity or damage; and any issues with the front window. These "
            "conditions are the Landlord's responsibility under the lease and Florida Statute "
            "&sect; 83.51.",
            styles["Body"],
        )
    )

    # Section 4
    story.append(Paragraph("4. MUTUAL RELEASE OF LIABILITY", styles["SectionHeading"]))
    story.append(
        Paragraph(
            "Upon execution of this Agreement, the Landlord and Tenants mutually release each other "
            "from all claims, duties, and liabilities arising under the original lease, including "
            "any early termination fee or liquidated damages under the lease's Early Termination "
            "Fee/Liquidated Damages Addendum. The move-out inspection shall apply solely to "
            "determining documented damage deductions from the second installment under Section 3 "
            "and shall not affect the termination or this mutual release.",
            styles["Body"],
        )
    )

    story.append(Spacer(1, 14))
    story.append(
        Paragraph(
            "IN WITNESS WHEREOF, the parties hereto have executed this Agreement:", styles["Body"]
        )
    )
    story.append(Spacer(1, 18))

    # Signature blocks
    line = "_______________________________________"

    def sig_block(name, role):
        sig = [
            [
                Paragraph(f"{line}", styles["Cell"]),
                Paragraph("_____________________", styles["Cell"]),
            ],
            [
                Paragraph(f"{name}, {role}", styles["CellBold"]),
                Paragraph("Date", styles["Cell"]),
            ],
        ]
        t = Table(sig, colWidths=[4.0 * inch, 2.5 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                    ("BOTTOMPADDING", (0, 1), (-1, 1), 16),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return t

    story.append(Paragraph("LANDLORD:", styles["SectionHeading"]))
    story.append(sig_block("Harry Sitbon", "Landlord"))

    story.append(Paragraph("TENANTS:", styles["SectionHeading"]))
    story.append(sig_block("Zachary Murray", "Tenant"))
    story.append(sig_block("Stephen Hakami-Yazdy", "Tenant"))

    return story


def main():
    styles = build_styles()
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=LETTER,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        title="Mutual Lease Termination Agreement and Release",
        author="Harry Sitbon",
    )
    doc.build(build_story(styles))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
