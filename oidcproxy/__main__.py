import oidcproxy


def main() -> None:
    app = oidcproxy.App()
    app.run()


if __name__ == "__main__":
    main()
