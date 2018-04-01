import socket
import tldextract


class DomainManager(object):

    @staticmethod
    def extract_domain(url):



        def get_full_domain(d_parsed):
            d_domain = [d_parsed.subdomain, d_parsed.domain, d_parsed.suffix]
            if d_parsed.subdomain and d_parsed.subdomain.lower() in []:
                del d_domain[0]

            if d_parsed.domain in ['co.uk',
                                    'co.in',
                                    'com.sg',
                                    'com.au',
                                    'org.in',
                                    'aol.com',
                                    'sweat.com',
                                    'com']:
                del domain[1]

            d_domain = filter(lambda i: i, d_domain)
            d_domain = ".".join(d_domain)
            return d_domain

        parsed = tldextract.extract(url)
        domain = get_full_domain(parsed)
        return domain

    @classmethod
    def is_domain_valid(cls, url):
        try:
            domain = cls.extract_domain(url)
            socket.gethostbyname(domain)
            return True
        except:
            try:
                parsed = tldextract.extract(url)
                domain = '.'.join(['www', parsed.registered_domain])
                socket.gethostbyname(domain)
                return True
            except:
                return False